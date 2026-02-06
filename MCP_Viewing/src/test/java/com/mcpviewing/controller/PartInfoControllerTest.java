package com.mcpviewing.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import com.mcpviewing.service.PartInfoService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Base64;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Unit tests for PartInfoController
 * Based on MIDGUARD project schema with composite key
 */
@WebMvcTest(PartInfoController.class)
class PartInfoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private PartInfoService partInfoService;

    private PartInfoRequest testRequest;
    private PartInfoResponse testResponse;
    private String testSachnummer;
    private Integer testRevision;
    private Integer testSequenz;
    private String testPlmxml;

    @BeforeEach
    void setUp() {
        testSachnummer = "TEST-SNR-001";
        testRevision = 1;
        testSequenz = 1;
        testPlmxml = Base64.getEncoder().encodeToString("<PLMXML>Test Data</PLMXML>".getBytes());

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
        testRequest.setPlmxml(testPlmxml);

        testResponse = new PartInfoResponse();
        testResponse.setObsoleteEntry((short) 0);
        testResponse.setClazz("TestClass");
        testResponse.setSachnummer(testSachnummer);
        testResponse.setRevision(testRevision);
        testResponse.setSequenz(testSequenz);
        testResponse.setOwner("TestOwner");
        testResponse.setStatus("Active");
        testResponse.setFrozen((short) 0);
        testResponse.setNomenclature("Test Part");
        testResponse.setChangeDescription("Initial version");
        testResponse.setChecksum3D(123456L);
        testResponse.setChecksum2D(789012L);
        testResponse.setChecksumBOM(345678L);
        testResponse.setPlmxml(testPlmxml);
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnPartInfo_WhenExists() throws Exception {
        // Arrange
        when(partInfoService.getLatestPartInfoBySachnummer(testSachnummer))
                .thenReturn(Optional.of(testResponse));

        String expectedFilename = String.format("%s_%d_%d.plmxml", testSachnummer, testRevision, testSequenz);
        byte[] expectedContent = Base64.getDecoder().decode(testPlmxml);

        // Act & Assert
        mockMvc.perform(get("/api/partinfo/{sachnummer}", testSachnummer))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/xml"))
                .andExpect(header().string("Content-Disposition", "form-data; name=\"attachment\"; filename=\"" + expectedFilename + "\""))
                .andExpect(content().bytes(expectedContent));

        verify(partInfoService, times(1)).getLatestPartInfoBySachnummer(testSachnummer);
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnNotFound_WhenNotExists() throws Exception {
        // Arrange
        when(partInfoService.getLatestPartInfoBySachnummer(testSachnummer))
                .thenReturn(Optional.empty());

        // Act & Assert
        mockMvc.perform(get("/api/partinfo/{sachnummer}", testSachnummer))
                .andExpect(status().isNotFound());

        verify(partInfoService, times(1)).getLatestPartInfoBySachnummer(testSachnummer);
    }

    @Test
    void getPartInfo_ShouldReturnPartInfo_WhenExists() throws Exception {
        // Arrange
        when(partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(Optional.of(testResponse));

        String expectedFilename = String.format("%s_%d_%d.plmxml", testSachnummer, testRevision, testSequenz);
        byte[] expectedContent = Base64.getDecoder().decode(testPlmxml);

        // Act & Assert
        mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/xml"))
                .andExpect(header().string("Content-Disposition", "form-data; name=\"attachment\"; filename=\"" + expectedFilename + "\""))
                .andExpect(content().bytes(expectedContent));

        verify(partInfoService, times(1)).getPartInfo(testSachnummer, testRevision, testSequenz);
    }

    @Test
    void getPartInfo_ShouldReturnNotFound_WhenNotExists() throws Exception {
        // Arrange
        when(partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(Optional.empty());

        // Act & Assert
        mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz))
                .andExpect(status().isNotFound());

        verify(partInfoService, times(1)).getPartInfo(testSachnummer, testRevision, testSequenz);
    }

    @Test
    void createOrUpdatePartInfo_ShouldReturnCreated_WhenNew() throws Exception {
        // Arrange
        when(partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(Optional.empty());
        when(partInfoService.createOrUpdatePartInfo(any(PartInfoRequest.class)))
                .thenReturn(testResponse);

        // Act & Assert
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sachnummer").value(testSachnummer))
                .andExpect(jsonPath("$.revision").value(testRevision))
                .andExpect(jsonPath("$.sequenz").value(testSequenz));

        verify(partInfoService, times(1)).createOrUpdatePartInfo(any(PartInfoRequest.class));
    }

    @Test
    void createOrUpdatePartInfo_ShouldReturnOk_WhenUpdating() throws Exception {
        // Arrange
        when(partInfoService.getPartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(Optional.of(testResponse));
        when(partInfoService.createOrUpdatePartInfo(any(PartInfoRequest.class)))
                .thenReturn(testResponse);

        // Act & Assert
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sachnummer").value(testSachnummer));

        verify(partInfoService, times(1)).createOrUpdatePartInfo(any(PartInfoRequest.class));
    }

    @Test
    void createOrUpdatePartInfo_ShouldReturnBadRequest_WhenInvalidData() throws Exception {
        // Arrange
        PartInfoRequest invalidRequest = new PartInfoRequest();
        invalidRequest.setSachnummer(""); // Invalid: blank sachnummer
        invalidRequest.setPlmxml(""); // Invalid: blank PLMXML
        invalidRequest.setClazz(""); // Invalid: blank clazz

        // Act & Assert
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void deletePartInfo_ShouldReturnNoContent_WhenExists() throws Exception {
        // Arrange
        when(partInfoService.deletePartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(true);

        // Act & Assert
        mockMvc.perform(delete("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNoContent());

        verify(partInfoService, times(1)).deletePartInfo(testSachnummer, testRevision, testSequenz);
    }

    @Test
    void deletePartInfo_ShouldReturnNotFound_WhenNotExists() throws Exception {
        // Arrange
        when(partInfoService.deletePartInfo(testSachnummer, testRevision, testSequenz))
                .thenReturn(false);

        // Act & Assert
        mockMvc.perform(delete("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());

        verify(partInfoService, times(1)).deletePartInfo(testSachnummer, testRevision, testSequenz);
    }
}
