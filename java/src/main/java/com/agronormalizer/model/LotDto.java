package com.agronormalizer.model;

import java.time.LocalDate;

public class LotDto {

    private String numeroLot;
    private LocalDate datePesee;
    private Double poidsCarcasseKg;
    private Double poidsDecoupeKg;
    private String categorieClassement;
    private String sourceBalance;

    public LotDto() {
    }

    public LotDto(String numeroLot, LocalDate datePesee, Double poidsCarcasseKg, Double poidsDecoupeKg,
            String categorieClassement, String sourceBalance) {
        this.numeroLot = numeroLot;
        this.datePesee = datePesee;
        this.poidsCarcasseKg = poidsCarcasseKg;
        this.poidsDecoupeKg = poidsDecoupeKg;
        this.categorieClassement = categorieClassement;
        this.sourceBalance = sourceBalance;
    }

    public String getNumeroLot() {
        return numeroLot;
    }

    public void setNumeroLot(String numeroLot) {
        this.numeroLot = numeroLot;
    }

    public LocalDate getDatePesee() {
        return datePesee;
    }

    public void setDatePesee(LocalDate datePesee) {
        this.datePesee = datePesee;
    }

    public Double getPoidsCarcasseKg() {
        return poidsCarcasseKg;
    }

    public void setPoidsCarcasseKg(Double poidsCarcasseKg) {
        this.poidsCarcasseKg = poidsCarcasseKg;
    }

    public Double getPoidsDecoupeKg() {
        return poidsDecoupeKg;
    }

    public void setPoidsDecoupeKg(Double poidsDecoupeKg) {
        this.poidsDecoupeKg = poidsDecoupeKg;
    }

    public String getCategorieClassement() {
        return categorieClassement;
    }

    public void setCategorieClassement(String categorieClassement) {
        this.categorieClassement = categorieClassement;
    }

    public String getSourceBalance() {
        return sourceBalance;
    }

    public void setSourceBalance(String sourceBalance) {
        this.sourceBalance = sourceBalance;
    }
}