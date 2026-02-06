package com.mcpviewing.mcp.tools;

import com.google.gson.JsonObject;
import com.mcpviewing.dto.PartInfoRequest;
import com.mcpviewing.dto.PartInfoResponse;
import com.mcpviewing.service.PartInfoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.*;

/**
 * Registry for MCP Tools
 * Handles tool definitions and execution
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ToolRegistry {

    private final PartInfoService partInfoService;

    /**
     * Get list of all available MCP tools
     */
    public List<McpTool> getTools() {
        List<McpTool> tools = new ArrayList<>();
        
        // Tool 1: Get latest PartInfo by Sachnummer
        tools.add(new McpTool(
            "get_partinfo_latest",
            "Retrieve the latest PLMXML data for a given part number (Sachnummer). Returns the version with the highest revision and sequence number.",
            createSchema(Map.of(
                "sachnummer", Map.of(
                    "type", "string",
                    "description", "Part number (Sachnummer) to retrieve"
                )
            ), List.of("sachnummer"))
        ));
        
        // Tool 2: Get specific PartInfo by composite key
        tools.add(new McpTool(
            "get_partinfo_specific",
            "Retrieve a specific version of PLMXML data using part number, revision, and sequence number.",
            createSchema(Map.of(
                "sachnummer", Map.of(
                    "type", "string",
                    "description", "Part number (Sachnummer)"
                ),
                "revision", Map.of(
                    "type", "integer",
                    "description", "Revision number"
                ),
                "sequenz", Map.of(
                    "type", "integer",
                    "description", "Sequence number"
                )
            ), List.of("sachnummer", "revision", "sequenz"))
        ));
        
        // Tool 3: Create or update PartInfo
        Map<String, Object> createPartInfoProperties = new HashMap<>();
        createPartInfoProperties.put("sachnummer", Map.of("type", "string", "description", "Part number (Sachnummer)"));
        createPartInfoProperties.put("revision", Map.of("type", "integer", "description", "Revision number"));
        createPartInfoProperties.put("sequenz", Map.of("type", "integer", "description", "Sequence number"));
        createPartInfoProperties.put("clazz", Map.of("type", "string", "description", "Part class (e.g., 'Part', 'Assembly')"));
        createPartInfoProperties.put("plmxml", Map.of("type", "string", "description", "Base64-encoded PLMXML content"));
        createPartInfoProperties.put("obsoleteEntry", Map.of("type", "integer", "description", "Optional: Obsolete entry flag (0 or 1)"));
        createPartInfoProperties.put("nomenclature", Map.of("type", "string", "description", "Optional: Part description/name"));
        createPartInfoProperties.put("owner", Map.of("type", "string", "description", "Optional: Owner/responsible person"));
        createPartInfoProperties.put("status", Map.of("type", "string", "description", "Optional: Status (e.g., 'Active', 'Obsolete')"));
        createPartInfoProperties.put("frozen", Map.of("type", "integer", "description", "Optional: Frozen flag (0 or 1)"));
        createPartInfoProperties.put("changeDescription", Map.of("type", "string", "description", "Optional: Description of changes"));
        createPartInfoProperties.put("checksum3D", Map.of("type", "integer", "description", "Optional: 3D model checksum"));
        createPartInfoProperties.put("checksum2D", Map.of("type", "integer", "description", "Optional: 2D drawing checksum"));
        createPartInfoProperties.put("checksumBOM", Map.of("type", "integer", "description", "Optional: Bill of Materials checksum"));
        
        tools.add(new McpTool(
            "create_partinfo",
            "Create or update PLMXML part information in the database. The PLMXML content must be Base64-encoded.",
            createSchema(createPartInfoProperties, List.of("sachnummer", "revision", "sequenz", "clazz", "plmxml"))
        ));
        
        // Tool 4: Delete PartInfo
        tools.add(new McpTool(
            "delete_partinfo",
            "Delete PLMXML part information from the database using the composite key.",
            createSchema(Map.of(
                "sachnummer", Map.of(
                    "type", "string",
                    "description", "Part number (Sachnummer)"
                ),
                "revision", Map.of(
                    "type", "integer",
                    "description", "Revision number"
                ),
                "sequenz", Map.of(
                    "type", "integer",
                    "description", "Sequence number"
                )
            ), List.of("sachnummer", "revision", "sequenz"))
        ));
        
        return tools;
    }

    /**
     * Execute a tool by name with given parameters
     */
    public Object executeTool(String toolName, JsonObject params) {
        log.debug("Executing tool: {} with params: {}", toolName, params);
        
        try {
            switch (toolName) {
                case "get_partinfo_latest":
                    return executeGetLatest(params);
                    
                case "get_partinfo_specific":
                    return executeGetSpecific(params);
                    
                case "create_partinfo":
                    return executeCreate(params);
                    
                case "delete_partinfo":
                    return executeDelete(params);
                    
                default:
                    throw new IllegalArgumentException("Unknown tool: " + toolName);
            }
        } catch (Exception e) {
            log.error("Error executing tool {}: {}", toolName, e.getMessage(), e);
            throw e;
        }
    }

    private Object executeGetLatest(JsonObject params) {
        String sachnummer = params.get("sachnummer").getAsString();
        Optional<PartInfoResponse> result = partInfoService.getLatestPartInfoBySachnummer(sachnummer);
        
        if (result.isPresent()) {
            return result.get();
        } else {
            return Map.of("error", "PartInfo not found for sachnummer: " + sachnummer);
        }
    }

    private Object executeGetSpecific(JsonObject params) {
        String sachnummer = params.get("sachnummer").getAsString();
        Integer revision = params.get("revision").getAsInt();
        Integer sequenz = params.get("sequenz").getAsInt();
        
        Optional<PartInfoResponse> result = partInfoService.getPartInfo(sachnummer, revision, sequenz);
        
        if (result.isPresent()) {
            return result.get();
        } else {
            return Map.of("error", String.format("PartInfo not found for sachnummer: %s, revision: %d, sequenz: %d", 
                sachnummer, revision, sequenz));
        }
    }

    private Object executeCreate(JsonObject params) {
        PartInfoRequest request = new PartInfoRequest();
        request.setSachnummer(params.get("sachnummer").getAsString());
        request.setRevision(params.get("revision").getAsInt());
        request.setSequenz(params.get("sequenz").getAsInt());
        request.setClazz(params.get("clazz").getAsString());
        request.setPlmxml(params.get("plmxml").getAsString());
        
        // Optional fields
        if (params.has("obsoleteEntry")) {
            request.setObsoleteEntry(params.get("obsoleteEntry").getAsShort());
        }
        if (params.has("nomenclature")) {
            request.setNomenclature(params.get("nomenclature").getAsString());
        }
        if (params.has("owner")) {
            request.setOwner(params.get("owner").getAsString());
        }
        if (params.has("status")) {
            request.setStatus(params.get("status").getAsString());
        }
        if (params.has("frozen")) {
            request.setFrozen(params.get("frozen").getAsShort());
        }
        if (params.has("changeDescription")) {
            request.setChangeDescription(params.get("changeDescription").getAsString());
        }
        if (params.has("checksum3D")) {
            request.setChecksum3D(params.get("checksum3D").getAsLong());
        }
        if (params.has("checksum2D")) {
            request.setChecksum2D(params.get("checksum2D").getAsLong());
        }
        if (params.has("checksumBOM")) {
            request.setChecksumBOM(params.get("checksumBOM").getAsLong());
        }
        
        return partInfoService.createOrUpdatePartInfo(request);
    }

    private Object executeDelete(JsonObject params) {
        String sachnummer = params.get("sachnummer").getAsString();
        Integer revision = params.get("revision").getAsInt();
        Integer sequenz = params.get("sequenz").getAsInt();
        
        boolean deleted = partInfoService.deletePartInfo(sachnummer, revision, sequenz);
        
        return Map.of(
            "success", deleted,
            "message", deleted ? "PartInfo deleted successfully" : "PartInfo not found"
        );
    }

    private Map<String, Object> createSchema(Map<String, Object> properties, List<String> required) {
        Map<String, Object> schema = new HashMap<>();
        schema.put("type", "object");
        schema.put("properties", properties);
        schema.put("required", required);
        return schema;
    }
}
