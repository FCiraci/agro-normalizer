package com.agronormalizer.model;

import java.time.LocalDate;

public class Lot {

    private String numeroLot;
    private LocalDate datePesee;
    private double poidsCarcasseKg;
    private double poidsDecoupeKg;
    private String categorieClassement;
    private String sourceBalance;

    public Lot(String numeroLot, LocalDate datePesee, double poidsCarcasseKg, double poidsDecoupeKg,
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

    public double getPoidsCarcasseKg() {
        return poidsCarcasseKg;
    }

    public void setPoidsCarcasseKg(double poidsCarcasseKg) {
        this.poidsCarcasseKg = poidsCarcasseKg;
    }

    public double getPoidsDecoupeKg() {
        return poidsDecoupeKg;
    }

    public void setPoidsDecoupeKg(double poidsDecoupeKg) {
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

    public String getId() {
        return numeroLot;
    }

    public double calculerRendement() {
        if (poidsCarcasseKg <= 0) {
            throw new IllegalStateException("Le poids de carcasse doit être supérieur à 0.");
        }
        return (poidsDecoupeKg / poidsCarcasseKg) * 100;
    }

    public boolean estEnAlerte(String espece) {
        double rendement = calculerRendement();

        if ("bovin".equalsIgnoreCase(espece)) {
            return rendement < 35.0 || rendement > 60.0;
        }

        if ("porc".equalsIgnoreCase(espece)) {
            return rendement < 60.0 || rendement > 85.0;
        }

        throw new IllegalArgumentException("Espèce inconnue: " + espece);
    }
}