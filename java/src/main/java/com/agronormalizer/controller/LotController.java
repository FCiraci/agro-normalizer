package com.agronormalizer.controller;

import com.agronormalizer.model.Lot;
import com.agronormalizer.model.LotDto;
import com.agronormalizer.service.LotService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/lots")
public class LotController {

    private final LotService lotService;

    public LotController(LotService lotService) {
        this.lotService = lotService;
    }

    @PostMapping
    public ResponseEntity<?> creerLot(@RequestBody LotDto lotDto) {
        try {
            Lot lot = lotService.creerLot(lotDto);
            Map<String, Object> reponse = new LinkedHashMap<>();
            reponse.put("id", lot.getId());
            reponse.put("rendement_pct", lot.calculerRendement());
            reponse.put("alerte", lot.estEnAlerte());
            reponse.put("lot", lotService.trouverLot(lot.getId()));
            return ResponseEntity.status(HttpStatus.CREATED).body(reponse);
        } catch (ResponseStatusException exception) {
            return ResponseEntity.status(exception.getStatusCode())
                    .body(Map.of("error", exception.getReason()));
        }
    }

    @GetMapping
    public ResponseEntity<List<LotDto>> listerLots() {
        return ResponseEntity.ok(lotService.listerLots());
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getLot(@PathVariable String id) {
        try {
            return ResponseEntity.ok(lotService.trouverLot(id));
        } catch (ResponseStatusException exception) {
            return ResponseEntity.status(exception.getStatusCode())
                    .body(Map.of("error", exception.getReason()));
        }
    }

    @GetMapping("/alertes")
    public ResponseEntity<List<LotDto>> getAlertes() {
        return ResponseEntity.ok(lotService.listerAlertes());
    }
}