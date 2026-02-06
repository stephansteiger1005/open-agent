package com.mcpviewing.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * JPA Entity representing PartInfo table
 * Based on MIDGUARD project schema - complete implementation
 */
@Entity
@Table(name = "PartInfo")
@IdClass(PartInfoId.class)
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PartInfo {

    @Column(name = "obsoleteEntry")
    private Short obsoleteEntry; // SMALLINT

    @NotBlank(message = "Clazz is required")
    @Column(name = "clazz", nullable = false, length = 16)
    private String clazz; // VARCHAR(16) NOT NULL

    @Id
    @NotBlank(message = "Sachnummer is required")
    @Column(name = "sachnummer", nullable = false, length = 32)
    private String sachnummer; // VARCHAR(32) NOT NULL, part of PRIMARY KEY

    @Id
    @NotNull(message = "Revision is required")
    @Column(name = "revision", nullable = false)
    private Integer revision; // INTEGER NOT NULL, part of PRIMARY KEY

    @Id
    @NotNull(message = "Sequenz is required")
    @Column(name = "sequenz", nullable = false)
    private Integer sequenz; // INTEGER NOT NULL, part of PRIMARY KEY

    @Column(name = "owner", length = 32)
    private String owner; // VARCHAR(32)

    @Column(name = "status", length = 16)
    private String status; // VARCHAR(16)

    @Column(name = "frozen")
    private Short frozen; // SMALLINT

    @Column(name = "nomenclature", length = 256)
    private String nomenclature; // VARCHAR(256)

    @Column(name = "changeDescription", length = 256)
    private String changeDescription; // VARCHAR(256)

    @Column(name = "checksum3D")
    private Long checksum3D; // BIGINT

    @Column(name = "checksum2D")
    private Long checksum2D; // BIGINT

    @Column(name = "checksumBOM")
    private Long checksumBOM; // BIGINT

    @Lob
    @Column(name = "plmxml")
    private byte[] plmxml; // BLOB - PLMXML content stored as zlib-compressed BLOB
}
