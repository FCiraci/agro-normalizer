package com.agronormalizer.model;

public class ApportMapper {

    public Apport toEntity(ApportDto dto) {
        return new Apport(
                dto.getNumeroApport(),
                dto.getDateApport(),
                dto.getSiteCollecte(),
                dto.getCereale(),
                dto.getPoidsNetKg(),
                dto.getTauxHumiditePct(),
                dto.getSourceSysteme());
    }

    public ApportDto toDto(Apport apport) {
        return new ApportDto(
                apport.getNumeroApport(),
                apport.getDateApport(),
                apport.getSiteCollecte(),
                apport.getCereale(),
                apport.getPoidsNetKg(),
                apport.getTauxHumiditePct(),
                apport.getSourceSysteme());
    }
}
