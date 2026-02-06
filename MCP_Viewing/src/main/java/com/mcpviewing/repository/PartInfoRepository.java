package com.mcpviewing.repository;

import com.mcpviewing.model.PartInfo;
import com.mcpviewing.model.PartInfoId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * JPA Repository for PartInfo entity
 * Provides CRUD operations for PartInfo table
 * Uses composite key (sachnummer, revision, sequenz)
 */
@Repository
public interface PartInfoRepository extends JpaRepository<PartInfo, PartInfoId> {
    
    /**
     * Find PartInfo with the highest revision and sequenz for a given sachnummer
     */
    @Query("SELECT p FROM PartInfo p WHERE p.sachnummer = :sachnummer " +
           "ORDER BY p.revision DESC, p.sequenz DESC LIMIT 1")
    Optional<PartInfo> findTopBySachnummerOrderByRevisionDescSequenzDesc(@Param("sachnummer") String sachnummer);
}
