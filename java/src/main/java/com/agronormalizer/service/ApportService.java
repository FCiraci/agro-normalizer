package com.agronormalizer.service;

import com.agronormalizer.model.Apport;
import com.agronormalizer.model.ApportDto;
import com.agronormalizer.model.ApportMapper;
import com.agronormalizer.repository.ApportRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
public class ApportService {

    private final ApportRepository apportRepository;
    private final ApportMapper apportMapper = new ApportMapper();

    public ApportService(ApportRepository apportRepository) {
        this.apportRepository = apportRepository;
    }

    public Apport creerApport(ApportDto dto) {
        verifierChampsObligatoires(dto);
        verifierValeurs(dto);

        Apport apport = apportMapper.toEntity(dto);
        apportRepository.save(apport);
        return apport;
    }

    public ApportDto trouverApport(String id) {
        Apport apport = apportRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Apport inconnu: " + id));
        return apportMapper.toDto(apport);
    }

    public List<ApportDto> listerApports() {
        return apportRepository.findAll().stream()
                .map(apportMapper::toDto)
                .toList();
    }

    public List<ApportDto> listerAlertes() {
        return apportRepository.findAlertes().stream()
                .map(apportMapper::toDto)
                .toList();
    }

    private void verifierChampsObligatoires(ApportDto dto) {
        verifierTexte(dto.getNumeroApport(), "numeroApport");
        if (dto.getDateApport() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: dateApport");
        }
        verifierTexte(dto.getSiteCollecte(), "siteCollecte");
        verifierTexte(dto.getCereale(), "cereale");
        if (dto.getPoidsNetKg() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: poidsNetKg");
        }
        if (dto.getTauxHumiditePct() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: tauxHumiditePct");
        }
        verifierTexte(dto.getSourceSysteme(), "sourceSysteme");
    }

    private void verifierValeurs(ApportDto dto) {
        if (dto.getPoidsNetKg() <= 0) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "poidsNetKg doit être strictement positif");
        }
        if (dto.getTauxHumiditePct() < 0 || dto.getTauxHumiditePct() > 100) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "tauxHumiditePct doit être compris entre 0 et 100");
        }
        if (!Apport.SEUILS_HUMIDITE.containsKey(dto.getCereale())) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "Céréale inconnue: " + dto.getCereale());
        }
    }

    private void verifierTexte(String valeur, String nomChamp) {
        if (valeur == null || valeur.isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Champ manquant: " + nomChamp);
        }
    }
}
