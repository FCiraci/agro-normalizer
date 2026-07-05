package com.agronormalizer.controller;

import com.agronormalizer.model.Apport;
import com.agronormalizer.model.ApportDto;
import com.agronormalizer.model.ApportMapper;
import com.agronormalizer.service.ApportService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/apports")
public class ApportController {

    private final ApportService apportService;
    private final ApportMapper apportMapper = new ApportMapper();

    public ApportController(ApportService apportService) {
        this.apportService = apportService;
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> creerApport(@RequestBody ApportDto apportDto) {
        Apport apport = apportService.creerApport(apportDto);
        Map<String, Object> reponse = new LinkedHashMap<>();
        reponse.put("id", apport.getId());
        reponse.put("alerte", apport.estEnAlerte());
        reponse.put("apport", apportMapper.toDto(apport));
        return ResponseEntity.status(HttpStatus.CREATED).body(reponse);
    }

    @GetMapping
    public ResponseEntity<List<ApportDto>> listerApports() {
        return ResponseEntity.ok(apportService.listerApports());
    }

    @GetMapping("/alertes")
    public ResponseEntity<List<ApportDto>> getAlertes() {
        return ResponseEntity.ok(apportService.listerAlertes());
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApportDto> getApport(@PathVariable String id) {
        return ResponseEntity.ok(apportService.trouverApport(id));
    }
}
