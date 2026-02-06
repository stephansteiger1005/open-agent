package com.mcpviewing.controller;

import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import com.mcpviewing.service.PartInfoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST Controller for PartInfo operations
 * Provides endpoints for managing PLMXML data in PartInfo table
 * Based on MIDGUARD project schema with composite key (sachnummer, revision, sequenz)
 */
@RestController
@RequestMapping("/api/partinfo")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "PartInfo API", description = "REST API for managing PLMXML data based on MIDGUARD schema")
public class PartInfoController {

    private final PartInfoService partInfoService;

    /**
     * Endpoint 1: Retrieve PLMXML by Sachnummer (latest revision/sequenz)
     */
    @GetMapping("/{sachnummer}")
    @Operation(
        summary = "Download PLMXML file by Sachnummer",
        description = "Downloads the PLMXML file for the latest version (highest revision and sequenz) of a given Sachnummer. The PLMXML is decompressed and returned as an XML file."
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Successfully downloaded PLMXML file",
            content = @Content(mediaType = "application/xml")
        ),
        @ApiResponse(responseCode = "404", description = "PartInfo not found for the given Sachnummer")
    })
    public ResponseEntity<byte[]> getLatestPartInfoBySachnummer(
            @Parameter(description = "Sachnummer (Part Number)", required = true)
            @PathVariable String sachnummer) {
        log.info("GET request for latest version of sachnummer: {}", sachnummer);
        
        return partInfoService.getLatestPartInfoBySachnummer(sachnummer)
                .map(response -> {
                    String filename = String.format("%s_%d_%d.plmxml", 
                        response.getSachnummer(), 
                        response.getRevision(), 
                        response.getSequenz());
                    
                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.APPLICATION_XML);
                    headers.setContentDispositionFormData("attachment", filename);
                    
                    byte[] plmxmlContent = java.util.Base64.getDecoder().decode(response.getPlmxml());
                    
                    return new ResponseEntity<>(plmxmlContent, headers, HttpStatus.OK);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Endpoint 2: Retrieve PLMXML by composite key (sachnummer, revision, sequenz)
     */
    @GetMapping("/{sachnummer}/{revision}/{sequenz}")
    @Operation(
        summary = "Download PLMXML file by composite key",
        description = "Downloads the PLMXML file for a given composite key (sachnummer, revision, sequenz). The PLMXML is decompressed and returned as an XML file."
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Successfully downloaded PLMXML file",
            content = @Content(mediaType = "application/xml")
        ),
        @ApiResponse(responseCode = "404", description = "PartInfo not found for the given composite key")
    })
    public ResponseEntity<byte[]> getPartInfo(
            @Parameter(description = "Sachnummer (Part Number)", required = true)
            @PathVariable String sachnummer,
            @Parameter(description = "Revision number", required = true)
            @PathVariable Integer revision,
            @Parameter(description = "Sequenz number", required = true)
            @PathVariable Integer sequenz) {
        log.info("GET request for sachnummer: {}, revision: {}, sequenz: {}", sachnummer, revision, sequenz);
        
        return partInfoService.getPartInfo(sachnummer, revision, sequenz)
                .map(response -> {
                    String filename = String.format("%s_%d_%d.plmxml", 
                        response.getSachnummer(), 
                        response.getRevision(), 
                        response.getSequenz());
                    
                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.APPLICATION_XML);
                    headers.setContentDispositionFormData("attachment", filename);
                    
                    byte[] plmxmlContent = java.util.Base64.getDecoder().decode(response.getPlmxml());
                    
                    return new ResponseEntity<>(plmxmlContent, headers, HttpStatus.OK);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Endpoint 3: Create or Update PartInfo with all MIDGUARD schema fields
     */
    @PostMapping
    @Operation(
        summary = "Create or Update PartInfo",
        description = "Creates a new PartInfo entry or updates an existing one. PLMXML data is provided as Base64-encoded string and stored as zlib-compressed BLOB."
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "PartInfo updated successfully",
            content = @Content(mediaType = "application/json", schema = @Schema(implementation = PartInfoResponse.class))
        ),
        @ApiResponse(
            responseCode = "201",
            description = "PartInfo created successfully",
            content = @Content(mediaType = "application/json", schema = @Schema(implementation = PartInfoResponse.class))
        ),
        @ApiResponse(responseCode = "400", description = "Invalid request data")
    })
    public ResponseEntity<PartInfoResponse> createOrUpdatePartInfo(
            @Valid @RequestBody PartInfoRequest request) {
        log.info("POST request to create/update PartInfo for sachnummer: {}, revision: {}, sequenz: {}", 
                 request.getSachnummer(), request.getRevision(), request.getSequenz());
        
        boolean exists = partInfoService.getPartInfo(
            request.getSachnummer(), 
            request.getRevision(), 
            request.getSequenz()
        ).isPresent();
        
        PartInfoResponse response = partInfoService.createOrUpdatePartInfo(request);
        
        if (exists) {
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        }
    }

    /**
     * Endpoint 4: Delete PartInfo by composite key (sachnummer, revision, sequenz)
     */
    @DeleteMapping("/{sachnummer}/{revision}/{sequenz}")
    @Operation(
        summary = "Delete PartInfo by composite key",
        description = "Deletes the PartInfo entry for the given composite key (sachnummer, revision, sequenz)"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "PartInfo deleted successfully"),
        @ApiResponse(responseCode = "404", description = "PartInfo not found for the given composite key")
    })
    public ResponseEntity<Void> deletePartInfo(
            @Parameter(description = "Sachnummer (Part Number)", required = true)
            @PathVariable String sachnummer,
            @Parameter(description = "Revision number", required = true)
            @PathVariable Integer revision,
            @Parameter(description = "Sequenz number", required = true)
            @PathVariable Integer sequenz) {
        log.info("DELETE request for sachnummer: {}, revision: {}, sequenz: {}", sachnummer, revision, sequenz);
        
        if (partInfoService.deletePartInfo(sachnummer, revision, sequenz)) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
