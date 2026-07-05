package com.agronormalizer.model;

public class LotMapper {

    public Lot toEntity(LotDto dto) {
        return new Lot(
                dto.getNumeroLot(),
                dto.getDatePesee(),
                dto.getPoidsCarcasseKg(),
                dto.getPoidsDecoupeKg(),
                dto.getCategorieClassement(),
                dto.getSourceBalance());
    }

    public LotDto toDto(Lot lot) {
        return new LotDto(
                lot.getNumeroLot(),
                lot.getDatePesee(),
                lot.getPoidsCarcasseKg(),
                lot.getPoidsDecoupeKg(),
                lot.getCategorieClassement(),
                lot.getSourceBalance());
    }
}