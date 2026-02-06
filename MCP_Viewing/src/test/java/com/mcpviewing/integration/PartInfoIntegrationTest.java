package com.mcpviewing.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for PartInfo API with embedded Derby database
 * Based on MIDGUARD project schema with composite key
 */
@SpringBootTest
@AutoConfigureMockMvc
class PartInfoIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private String testSachnummer;
    private Integer testRevision;
    private Integer testSequenz;
    private String testPlmxml;
    private String expectedPlmxmlContent;
    private PartInfoRequest testRequest;

    @BeforeEach
    void setUp() {
        testSachnummer = "INTEGRATION-TEST-" + System.currentTimeMillis();
        testRevision = 1;
        testSequenz = 1;
        expectedPlmxmlContent = "<PLMXML><Part id='123'>Test Part</Part></PLMXML>";
        testPlmxml = Base64.getEncoder().encodeToString(expectedPlmxmlContent.getBytes());

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
    }

    @Test
    void fullCrudOperations_ShouldWorkCorrectly() throws Exception {
        // 1. Create new PartInfo
        MvcResult createResult = mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sachnummer").value(testSachnummer))
                .andExpect(jsonPath("$.revision").value(testRevision))
                .andExpect(jsonPath("$.sequenz").value(testSequenz))
                .andReturn();

        PartInfoResponse createdResponse = objectMapper.readValue(
                createResult.getResponse().getContentAsString(),
                PartInfoResponse.class
        );
        assertThat(createdResponse.getSachnummer()).isEqualTo(testSachnummer);

        // 2. Retrieve the created PartInfo (as file download)
        MvcResult getResult = mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/xml"))
                .andExpect(header().exists("Content-Disposition"))
                .andReturn();

        // Verify the downloaded PLMXML content
        byte[] downloadedContent = getResult.getResponse().getContentAsByteArray();
        String downloadedPlmxml = new String(downloadedContent);
        assertThat(downloadedPlmxml).isEqualTo(expectedPlmxmlContent);

        // 3. Update the PartInfo (same composite key, different fields)
        testRequest.setStatus("Updated");
        testRequest.setNomenclature("Updated Part");

        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sachnummer").value(testSachnummer))
                .andExpect(jsonPath("$.status").value("Updated"))
                .andExpect(jsonPath("$.nomenclature").value("Updated Part"));

        // 4. Verify the update (by downloading the file)
        MvcResult verifyResult = mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/xml"))
                .andReturn();

        // The PLMXML content should still be the same
        byte[] verifyContent = verifyResult.getResponse().getContentAsByteArray();
        String verifyPlmxml = new String(verifyContent);
        assertThat(verifyPlmxml).isEqualTo(expectedPlmxmlContent);

        // 5. Delete the PartInfo
        mockMvc.perform(delete("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNoContent());

        // 6. Verify deletion
        mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz))
                .andExpect(status().isNotFound());

        // 7. Verify second delete returns not found
        mockMvc.perform(delete("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        testSachnummer, testRevision, testSequenz)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound());
    }

    @Test
    void createPartInfo_WithValidData_ShouldSucceed() throws Exception {
        String uniqueSachnummer = "CREATE-TEST-" + System.currentTimeMillis();
        testRequest.setSachnummer(uniqueSachnummer);
        testRequest.setRevision(2);
        testRequest.setSequenz(2);

        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.sachnummer").value(uniqueSachnummer));
    }

    @Test
    void getPartInfo_WithNonExistentKey_ShouldReturnNotFound() throws Exception {
        mockMvc.perform(get("/api/partinfo/{sachnummer}/{revision}/{sequenz}", 
                        "NON-EXISTENT-SNR", 999, 999))
                .andExpect(status().isNotFound());
    }

    @Test
    void createPartInfo_WithInvalidData_ShouldReturnBadRequest() throws Exception {
        PartInfoRequest invalidRequest = new PartInfoRequest();
        invalidRequest.setSachnummer(""); // Invalid: blank sachnummer
        invalidRequest.setClazz(""); // Invalid: blank clazz
        invalidRequest.setPlmxml(""); // Invalid: blank PLMXML

        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnLatestVersion() throws Exception {
        // Create multiple versions of the same part
        String sachnummer = "LATEST-TEST-" + System.currentTimeMillis();
        
        // Create version 1.1
        testRequest.setSachnummer(sachnummer);
        testRequest.setRevision(1);
        testRequest.setSequenz(1);
        testRequest.setStatus("Old");
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated());

        // Create version 1.2
        testRequest.setSequenz(2);
        testRequest.setStatus("Newer");
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated());

        // Create version 2.1 (this should be the latest)
        testRequest.setRevision(2);
        testRequest.setSequenz(1);
        testRequest.setStatus("Latest");
        mockMvc.perform(post("/api/partinfo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(testRequest)))
                .andExpect(status().isCreated());

        // Retrieve latest version (should get 2.1) as file download
        MvcResult latestResult = mockMvc.perform(get("/api/partinfo/{sachnummer}", sachnummer))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/xml"))
                .andExpect(header().string("Content-Disposition", "form-data; name=\"attachment\"; filename=\"" + sachnummer + "_2_1.plmxml\""))
                .andReturn();

        // Verify the downloaded PLMXML content
        byte[] latestContent = latestResult.getResponse().getContentAsByteArray();
        String latestPlmxml = new String(latestContent);
        assertThat(latestPlmxml).isEqualTo(expectedPlmxmlContent);
    }

    @Test
    void getLatestPartInfoBySachnummer_ShouldReturnNotFound_WhenNotExists() throws Exception {
        mockMvc.perform(get("/api/partinfo/{sachnummer}", "NON-EXISTENT"))
                .andExpect(status().isNotFound());
    }
}
