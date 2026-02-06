package com.mcpviewing.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for PartInfo
 * Based on MIDGUARD project schema
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PartInfoResponse {

    private Short obsoleteEntry; // SMALLINT

    private String clazz; // VARCHAR(16) NOT NULL

    private String sachnummer; // VARCHAR(32) NOT NULL

    private Integer revision; // INTEGER NOT NULL

    private Integer sequenz; // INTEGER NOT NULL

    private String owner; // VARCHAR(32)

    private String status; // VARCHAR(16)

    private Short frozen; // SMALLINT

    private String nomenclature; // VARCHAR(256)

    private String changeDescription; // VARCHAR(256)

    private Long checksum3D; // BIGINT

    private Long checksum2D; // BIGINT

    private Long checksumBOM; // BIGINT

    private String plmxml; // Base64 encoded PLMXML content (decompressed from zlib storage)
}
