package com.mcpviewing.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for creating or updating PartInfo
 * Based on MIDGUARD project schema
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PartInfoRequest {

    private Short obsoleteEntry; // SMALLINT

    @NotBlank(message = "Clazz is required")
    private String clazz; // VARCHAR(16) NOT NULL

    @NotBlank(message = "Sachnummer is required")
    private String sachnummer; // VARCHAR(32) NOT NULL

    @NotNull(message = "Revision is required")
    private Integer revision; // INTEGER NOT NULL

    @NotNull(message = "Sequenz is required")
    private Integer sequenz; // INTEGER NOT NULL

    private String owner; // VARCHAR(32)

    private String status; // VARCHAR(16)

    private Short frozen; // SMALLINT

    private String nomenclature; // VARCHAR(256)

    private String changeDescription; // VARCHAR(256)

    private Long checksum3D; // BIGINT

    private Long checksum2D; // BIGINT

    private Long checksumBOM; // BIGINT

    @NotBlank(message = "PLMXML content is required")
    private String plmxml; // Base64 encoded PLMXML content (will be compressed with zlib before storage)
}
