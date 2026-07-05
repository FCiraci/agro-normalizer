package com.agronormalizer.repository;

import com.agronormalizer.model.Lot;

import java.util.List;
import java.util.Optional;

public interface LotRepository {
    void save(Lot lot);

    Optional<Lot> findById(String id);

    List<Lot> findAll();

    List<Lot> findAlertes(); // ← à implémenter avec Stream + filter
}
