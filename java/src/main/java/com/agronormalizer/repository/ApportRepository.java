package com.agronormalizer.repository;

import com.agronormalizer.model.Apport;

import java.util.List;
import java.util.Optional;

public interface ApportRepository {
    void save(Apport apport);

    Optional<Apport> findById(String id);

    List<Apport> findAll();

    List<Apport> findAlertes();
}
