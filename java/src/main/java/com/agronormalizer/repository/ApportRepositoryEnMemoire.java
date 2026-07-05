package com.agronormalizer.repository;

import com.agronormalizer.model.Apport;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class ApportRepositoryEnMemoire implements ApportRepository {

    private final Map<String, Apport> apports = new ConcurrentHashMap<>();

    @Override
    public void save(Apport apport) {
        apports.put(apport.getId(), apport);
    }

    @Override
    public Optional<Apport> findById(String id) {
        return Optional.ofNullable(apports.get(id));
    }

    @Override
    public List<Apport> findAll() {
        return new ArrayList<>(apports.values());
    }

    @Override
    public List<Apport> findAlertes() {
        return apports.values().stream()
                .filter(Apport::estEnAlerte)
                .toList();
    }
}
