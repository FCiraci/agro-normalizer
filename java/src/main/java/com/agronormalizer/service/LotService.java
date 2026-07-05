package com.agronormalizer.service;

import com.agronormalizer.model.Lot;
import com.agronormalizer.model.LotDto;
import com.agronormalizer.model.LotMapper;
import com.agronormalizer.repository.LotRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
public class LotService {

    private final LotRepository lotRepository;
    private final LotMapper lotMapper = new LotMapper();

    public LotService(LotRepository lotRepository) {
        this.lotRepository = lotRepository;
    }

    public Lot creerLot(LotDto dto) {
        verifierChampsObligatoires(dto);
        verifierPoids(dto);

        Lot lot = lotMapper.toEntity(dto);
        lotRepository.save(lot);
        return lot;
    }

    public LotDto trouverLot(String id) {
        Lot lot = lotRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Lot inconnu: " + id));
        return lotMapper.toDto(lot);
    }

    public List<LotDto> listerAlertes() {
        return lotRepository.findAlertes().stream()
                .map(lotMapper::toDto)
                .toList();
    }

    private void verifierChampsObligatoires(LotDto dto) {
        verifierTexte(dto.getNumeroLot(), "numeroLot");
        if (dto.getDatePesee() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: datePesee");
        }
        if (dto.getPoidsCarcasseKg() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: poidsCarcasseKg");
        }
        if (dto.getPoidsDecoupeKg() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: poidsDecoupeKg");
        }
        verifierTexte(dto.getCategorieClassement(), "categorieClassement");
        verifierTexte(dto.getSourceBalance(), "sourceBalance");
    }

    private void verifierPoids(LotDto dto) {
        if (dto.getPoidsCarcasseKg() == null || dto.getPoidsCarcasseKg() <= 0) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "poidsCarcasseKg doit être strictement positif");
        }
        if (dto.getPoidsDecoupeKg() == null || dto.getPoidsDecoupeKg() <= 0) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "poidsDecoupeKg doit être strictement positif");
        }
    }

    private void verifierTexte(String valeur, String nomChamp) {
        if (valeur == null || valeur.isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: " + nomChamp);
        }
    }
}