package com.agronormalizer.repository;

import com.agronormalizer.model.Lot;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class LotRepositoryEnMemoire implements LotRepository {

    private final Map<String, Lot> lots = new HashMap<>();

    @Override
    public void save(Lot lot) {
        lots.put(lot.getId(), lot);
    }

    @Override
    public Optional<Lot> findById(String id) {
        return Optional.ofNullable(lots.get(id));
    }

    @Override
    public List<Lot> findAll() {
        return new ArrayList<>(lots.values());
    }

    @Override
    public List<Lot> findAlertes() {
        return lots.values().stream()
                .filter(lot -> lot.estEnAlerte("bovin"))
                .collect(Collectors.toList());
    }
}
