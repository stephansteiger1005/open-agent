package com.mcpviewing.service;

import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import com.mcpviewing.model.PartInfo;
import com.mcpviewing.model.PartInfoId;
import com.mcpviewing.repository.PartInfoRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;
import java.util.Optional;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;

/**
 * Service layer for PartInfo operations
 * Handles business logic for PLMXML data management
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PartInfoService {

    private final PartInfoRepository partInfoRepository;

    /**
     * Retrieve PartInfo by composite key (sachnummer, revision, sequenz)
     */
    @Transactional(readOnly = true)
    public Optional<PartInfoResponse> getPartInfo(String sachnummer, Integer revision, Integer sequenz) {
        log.debug("Fetching PartInfo for sachnummer: {}, revision: {}, sequenz: {}", sachnummer, revision, sequenz);
        PartInfoId id = new PartInfoId(sachnummer, revision, sequenz);
        return partInfoRepository.findById(id)
                .map(this::convertToResponse);
    }

    /**
     * Retrieve PartInfo with the highest revision and sequenz for a given sachnummer
     */
    @Transactional(readOnly = true)
    public Optional<PartInfoResponse> getLatestPartInfoBySachnummer(String sachnummer) {
        log.debug("Fetching latest PartInfo for sachnummer: {}", sachnummer);
        return partInfoRepository.findTopBySachnummerOrderByRevisionDescSequenzDesc(sachnummer)
                .map(this::convertToResponse);
    }

    /**
     * Create or update PartInfo
     */
    @Transactional
    public PartInfoResponse createOrUpdatePartInfo(PartInfoRequest request) {
        log.debug("Creating/Updating PartInfo for sachnummer: {}, revision: {}, sequenz: {}", 
                  request.getSachnummer(), request.getRevision(), request.getSequenz());
        
        PartInfoId id = new PartInfoId(request.getSachnummer(), request.getRevision(), request.getSequenz());
        PartInfo partInfo = partInfoRepository.findById(id)
                .orElse(new PartInfo());
        
        // Set all fields from the MIDGUARD schema
        partInfo.setObsoleteEntry(request.getObsoleteEntry());
        partInfo.setClazz(request.getClazz());
        partInfo.setSachnummer(request.getSachnummer());
        partInfo.setRevision(request.getRevision());
        partInfo.setSequenz(request.getSequenz());
        partInfo.setOwner(request.getOwner());
        partInfo.setStatus(request.getStatus());
        partInfo.setFrozen(request.getFrozen());
        partInfo.setNomenclature(request.getNomenclature());
        partInfo.setChangeDescription(request.getChangeDescription());
        partInfo.setChecksum3D(request.getChecksum3D());
        partInfo.setChecksum2D(request.getChecksum2D());
        partInfo.setChecksumBOM(request.getChecksumBOM());
        
        try {
            // Decode Base64 to get the original PLMXML content
            byte[] decodedPlmxml = Base64.getDecoder().decode(request.getPlmxml());
            
            // Compress the PLMXML data using zlib (Deflater)
            byte[] compressedPlmxml = compressZlib(decodedPlmxml);
            
            partInfo.setPlmxml(compressedPlmxml);
        } catch (IllegalArgumentException e) {
            log.error("Invalid Base64 encoding for PLMXML data: {}", e.getMessage());
            throw new IllegalArgumentException("PLMXML must be valid Base64 encoded data", e);
        } catch (IOException e) {
            log.error("Error compressing PLMXML data: {}", e.getMessage());
            throw new RuntimeException("Failed to compress PLMXML data", e);
        }
        
        PartInfo savedPartInfo = partInfoRepository.save(partInfo);
        log.info("PartInfo saved successfully for sachnummer: {}, revision: {}, sequenz: {}", 
                 savedPartInfo.getSachnummer(), savedPartInfo.getRevision(), savedPartInfo.getSequenz());
        
        return convertToResponse(savedPartInfo);
    }

    /**
     * Delete PartInfo by composite key (sachnummer, revision, sequenz)
     */
    @Transactional
    public boolean deletePartInfo(String sachnummer, Integer revision, Integer sequenz) {
        log.debug("Deleting PartInfo for sachnummer: {}, revision: {}, sequenz: {}", sachnummer, revision, sequenz);
        
        PartInfoId id = new PartInfoId(sachnummer, revision, sequenz);
        if (partInfoRepository.existsById(id)) {
            partInfoRepository.deleteById(id);
            log.info("PartInfo deleted successfully for sachnummer: {}, revision: {}, sequenz: {}", 
                     sachnummer, revision, sequenz);
            return true;
        }
        
        log.warn("PartInfo not found for sachnummer: {}, revision: {}, sequenz: {}", 
                 sachnummer, revision, sequenz);
        return false;
    }

    /**
     * Convert PartInfo entity to PartInfoResponse DTO
     */
    private PartInfoResponse convertToResponse(PartInfo partInfo) {
        PartInfoResponse response = new PartInfoResponse();
        response.setObsoleteEntry(partInfo.getObsoleteEntry());
        response.setClazz(partInfo.getClazz());
        response.setSachnummer(partInfo.getSachnummer());
        response.setRevision(partInfo.getRevision());
        response.setSequenz(partInfo.getSequenz());
        response.setOwner(partInfo.getOwner());
        response.setStatus(partInfo.getStatus());
        response.setFrozen(partInfo.getFrozen());
        response.setNomenclature(partInfo.getNomenclature());
        response.setChangeDescription(partInfo.getChangeDescription());
        response.setChecksum3D(partInfo.getChecksum3D());
        response.setChecksum2D(partInfo.getChecksum2D());
        response.setChecksumBOM(partInfo.getChecksumBOM());
        
        try {
            // Decompress the zlib-compressed PLMXML data
            byte[] decompressedPlmxml = decompressZlib(partInfo.getPlmxml());
            
            // Encode to Base64 for API response
            response.setPlmxml(Base64.getEncoder().encodeToString(decompressedPlmxml));
        } catch (DataFormatException | IOException e) {
            log.error("Error decompressing PLMXML data for sachnummer {}: {}", partInfo.getSachnummer(), e.getMessage());
            throw new RuntimeException("Failed to decompress PLMXML data", e);
        }
        
        return response;
    }
    
    /**
     * Compress data using zlib (Deflater)
     */
    private byte[] compressZlib(byte[] data) throws IOException {
        Deflater deflater = new Deflater();
        deflater.setInput(data);
        deflater.finish();
        
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream(data.length);
        byte[] buffer = new byte[1024];
        
        while (!deflater.finished()) {
            int count = deflater.deflate(buffer);
            outputStream.write(buffer, 0, count);
        }
        
        outputStream.close();
        deflater.end();
        
        byte[] compressedData = outputStream.toByteArray();
        log.debug("Compressed {} bytes to {} bytes (ratio: {:.2f}%)", 
                  data.length, compressedData.length, 
                  String.format("%.2f", 100.0 * compressedData.length / data.length));
        
        return compressedData;
    }
    
    /**
     * Decompress zlib-compressed data using Inflater
     */
    private byte[] decompressZlib(byte[] compressedData) throws DataFormatException, IOException {
        Inflater inflater = new Inflater();
        inflater.setInput(compressedData);
        
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream(compressedData.length);
        byte[] buffer = new byte[1024];
        
        while (!inflater.finished()) {
            int count = inflater.inflate(buffer);
            outputStream.write(buffer, 0, count);
        }
        
        outputStream.close();
        inflater.end();
        
        byte[] decompressedData = outputStream.toByteArray();
        log.debug("Decompressed {} bytes to {} bytes", compressedData.length, decompressedData.length);
        
        return decompressedData;
    }
}
