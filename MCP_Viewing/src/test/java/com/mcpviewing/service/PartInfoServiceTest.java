package com.mcpviewing.service;

import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import com.mcpviewing.model.PartInfo;
import com.mcpviewing.model.PartInfoId;
import com.mcpviewing.repository.PartInfoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Base64;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import java.io.ByteArrayOutputStream;
import java.util.zip.Deflater;

/**
 * Unit tests for PartInfoService
 * Based on MIDGUARD project schema with composite key
 */
@ExtendWith(MockitoExtension.class)
class PartInfoServiceTest {

    @Mock
    private PartInfoRepository partInfoRepository;

    @InjectMocks
    private PartInfoService partInfoService;

    private PartInfo testPartInfo;
    private PartInfoRequest testRequest;
    private String testSachnummer;
    private Integer testRevision;
    private Integer testSequenz;
    private PartInfoId testId;

    @BeforeEach
    void setUp() throws Exception {
        testSachnummer = "TEST-SNR-001";
        testRevision = 1;
        testSequenz = 1;
        testId = new PartInfoId(testSachnummer, testRevision, testSequenz);
        
        byte[] plmxmlBytes = "<PLMXML>Test Data</PLMXML>".getBytes();

        // Compress the data for storage (simulating what the service does)
        byte[] compressedPlmxml = compressZlib(plmxmlBytes);

        testPartInfo = new PartInfo();
        testPartInfo.setObsoleteEntry((short) 0);
        testPartInfo.setClazz("TestClass");
        testPartInfo.setSachnummer(testSachnummer);
        testPartInfo.setRevision(testRevision);
        testPartInfo.setSequenz(testSequenz);
        testPartInfo.setOwner("TestOwner");
        testPartInfo.setStatus("Active");
        testPartInfo.setFrozen((short) 0);
        testPartInfo.setNomenclature("Test Part");
        testPartInfo.setChangeDescription("Initial version");
        testPartInfo.setChecksum3D(123456L);
        testPartInfo.setChecksum2D(789012L);
        testPartInfo.setChecksumBOM(345678L);
        testPartInfo.setPlmxml(compressedPlmxml);  // Store compressed data

        testRequest = new PartInfoRequest();
        testRequest.setObsoleteEntry((short) 0);
        testRequest.setClazz("TestClass");
        testRequest.setSachnummer(testSachnummer);
        testRequest.setRevision(testRevision);
        testRequest.setSequenz(testSequenz);
        testRequest.setOwner("TestOwner");
        testRequest.setStatus("Active");
        testRequest.setFrozen((short) 0);
        testRequest.setNomenclature("Test Part");
        testRequest.setChangeDescription("Initial version");
        testRequest.setChecksum3D(123456L);
        testRequest.setChecksum2D(789012L);
        testRequest.setChecksumBOM(345678L);
        testRequest.setPlmxml(Base64.getEncoder().encodeToString(plmxmlBytes));  // Request has uncompressed Base64
    }
    
    /**
     * Helper method to compress data using zlib (same as in the service)
     */
    private byte[] compressZlib(byte[] data) throws Exception {
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
        
        return outputStream.toByteArray();
    }

    @Test
    void getPartInfo_ShouldReturnPartInfo_WhenExists() {
        // Arrange
        when(partInfoRepository.findById(testId)).thenReturn(Optional.of(testPartInfo));

        // Act
        Optional<PartInfoResponse> result = partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getSachnummer()).isEqualTo(testSachnummer);
        assertThat(result.get().getRevision()).isEqualTo(testRevision);
        assertThat(result.get().getSequenz()).isEqualTo(testSequenz);
        verify(partInfoRepository, times(1)).findById(any(PartInfoId.class));
    }

    @Test
    void getPartInfo_ShouldReturnEmpty_WhenNotExists() {
        // Arrange
        when(partInfoRepository.findById(any(PartInfoId.class))).thenReturn(Optional.empty());

        // Act
        Optional<PartInfoResponse> result = partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz);

        // Assert
        assertThat(result).isEmpty();
        verify(partInfoRepository, times(1)).findById(any(PartInfoId.class));
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnPartInfo_WhenExists() {
        // Arrange
        when(partInfoRepository.findTopBySachnummerOrderByRevisionDescSequenzDesc(testSachnummer))
                .thenReturn(Optional.of(testPartInfo));

        // Act
        Optional<PartInfoResponse> result = partInfoService.getLatestPartInfoBySachnummer(testSachnummer);

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getSachnummer()).isEqualTo(testSachnummer);
        assertThat(result.get().getRevision()).isEqualTo(testRevision);
        assertThat(result.get().getSequenz()).isEqualTo(testSequenz);
        verify(partInfoRepository, times(1)).findTopBySachnummerOrderByRevisionDescSequenzDesc(testSachnummer);
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnEmpty_WhenNotExists() {
        // Arrange
        when(partInfoRepository.findTopBySachnummerOrderByRevisionDescSequenzDesc(testSachnummer))
                .thenReturn(Optional.empty());

        // Act
        Optional<PartInfoResponse> result = partInfoService.getLatestPartInfoBySachnummer(testSachnummer);

        // Assert
        assertThat(result).isEmpty();
        verify(partInfoRepository, times(1)).findTopBySachnummerOrderByRevisionDescSequenzDesc(testSachnummer);
    }

    @Test
    void createOrUpdatePartInfo_ShouldCreateNew_WhenNotExists() {
        // Arrange
        when(partInfoRepository.findById(any(PartInfoId.class))).thenReturn(Optional.empty());
        when(partInfoRepository.save(any(PartInfo.class))).thenReturn(testPartInfo);

        // Act
        PartInfoResponse result = partInfoService.createOrUpdatePartInfo(testRequest);

        // Assert
        assertThat(result.getSachnummer()).isEqualTo(testSachnummer);
        assertThat(result.getRevision()).isEqualTo(testRevision);
        assertThat(result.getSequenz()).isEqualTo(testSequenz);
        verify(partInfoRepository, times(1)).save(any(PartInfo.class));
    }

    @Test
    void createOrUpdatePartInfo_ShouldUpdate_WhenExists() {
        // Arrange
        when(partInfoRepository.findById(any(PartInfoId.class))).thenReturn(Optional.of(testPartInfo));
        when(partInfoRepository.save(any(PartInfo.class))).thenReturn(testPartInfo);

        testRequest.setStatus("Updated");

        // Act
        PartInfoResponse result = partInfoService.createOrUpdatePartInfo(testRequest);

        // Assert
        assertThat(result.getSachnummer()).isEqualTo(testSachnummer);
        verify(partInfoRepository, times(1)).save(any(PartInfo.class));
    }

    @Test
    void deletePartInfo_ShouldReturnTrue_WhenExists() {
        // Arrange
        when(partInfoRepository.existsById(any(PartInfoId.class))).thenReturn(true);
        doNothing().when(partInfoRepository).deleteById(any(PartInfoId.class));

        // Act
        boolean result = partInfoService.deletePartInfo(testSachnummer, testRevision, testSequenz);

        // Assert
        assertThat(result).isTrue();
        verify(partInfoRepository, times(1)).existsById(any(PartInfoId.class));
        verify(partInfoRepository, times(1)).deleteById(any(PartInfoId.class));
    }

    @Test
    void deletePartInfo_ShouldReturnFalse_WhenNotExists() {
        // Arrange
        when(partInfoRepository.existsById(any(PartInfoId.class))).thenReturn(false);

        // Act
        boolean result = partInfoService.deletePartInfo(testSachnummer, testRevision, testSequenz);

        // Assert
        assertThat(result).isFalse();
        verify(partInfoRepository, times(1)).existsById(any(PartInfoId.class));
        verify(partInfoRepository, never()).deleteById(any());
    }

    @Test
    void createOrUpdatePartInfo_ShouldThrowException_WhenInvalidBase64() {
        // Arrange
        testRequest.setPlmxml("This is not valid Base64!!!");

        // Act & Assert
        assertThatThrownBy(() -> partInfoService.createOrUpdatePartInfo(testRequest))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("PLMXML must be valid Base64 encoded data");
    }
}
