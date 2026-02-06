package com.mcpviewing.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Composite Primary Key for PartInfo entity
 * Based on MIDGUARD project schema
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PartInfoId implements Serializable {
    
    private String sachnummer;
    private Integer revision;
    private Integer sequenz;
}
