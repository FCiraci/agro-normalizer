package com.agronormalizer.model;

public class LotMapper {

    public Lot toEntity(LotDto dto) {
        String espece = dto.getEspece() == null || dto.getEspece().isBlank()
                ? Lot.ESPECE_PAR_DEFAUT
                : dto.getEspece().trim().toLowerCase();
        return new Lot(
                dto.getNumeroLot(),
                dto.getDatePesee(),
                dto.getPoidsCarcasseKg(),
                dto.getPoidsDecoupeKg(),
                dto.getCategorieClassement(),
                dto.getSourceBalance(),
                espece);
    }

    public LotDto toDto(Lot lot) {
        return new LotDto(
                lot.getNumeroLot(),
                lot.getDatePesee(),
                lot.getPoidsCarcasseKg(),
                lot.getPoidsDecoupeKg(),
                lot.getCategorieClassement(),
                lot.getSourceBalance(),
                lot.getEspece());
    }
}