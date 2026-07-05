package com.agronormalizer.model;

import java.time.LocalDate;
import java.util.Map;

public class Apport {

    // Seuils identiques à SEUILS_HUMIDITE dans python/models/apport_cereale.py.
    public static final Map<String, Double> SEUILS_HUMIDITE = Map.of(
            "ble_tendre", 15.0,
            "mais", 14.0,
            "orge", 14.5);

    private String numeroApport;
    private LocalDate dateApport;
    private String siteCollecte;
    private String cereale;
    private double poidsNetKg;
    private double tauxHumiditePct;
    private String sourceSysteme;

    public Apport(String numeroApport, LocalDate dateApport, String siteCollecte, String cereale,
            double poidsNetKg, double tauxHumiditePct, String sourceSysteme) {
        this.numeroApport = numeroApport;
        this.dateApport = dateApport;
        this.siteCollecte = siteCollecte;
        this.cereale = cereale;
        this.poidsNetKg = poidsNetKg;
        this.tauxHumiditePct = tauxHumiditePct;
        this.sourceSysteme = sourceSysteme;
    }

    public String getNumeroApport() {
        return numeroApport;
    }

    public void setNumeroApport(String numeroApport) {
        this.numeroApport = numeroApport;
    }

    public LocalDate getDateApport() {
        return dateApport;
    }

    public void setDateApport(LocalDate dateApport) {
        this.dateApport = dateApport;
    }

    public String getSiteCollecte() {
        return siteCollecte;
    }

    public void setSiteCollecte(String siteCollecte) {
        this.siteCollecte = siteCollecte;
    }

    public String getCereale() {
        return cereale;
    }

    public void setCereale(String cereale) {
        this.cereale = cereale;
    }

    public double getPoidsNetKg() {
        return poidsNetKg;
    }

    public void setPoidsNetKg(double poidsNetKg) {
        this.poidsNetKg = poidsNetKg;
    }

    public double getTauxHumiditePct() {
        return tauxHumiditePct;
    }

    public void setTauxHumiditePct(double tauxHumiditePct) {
        this.tauxHumiditePct = tauxHumiditePct;
    }

    public String getSourceSysteme() {
        return sourceSysteme;
    }

    public void setSourceSysteme(String sourceSysteme) {
        this.sourceSysteme = sourceSysteme;
    }

    public String getId() {
        return numeroApport;
    }

    public boolean estEnAlerte() {
        Double seuilMax = SEUILS_HUMIDITE.get(cereale);
        if (seuilMax == null) {
            throw new IllegalArgumentException("Céréale inconnue: " + cereale);
        }
        return tauxHumiditePct > seuilMax;
    }
}
