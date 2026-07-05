package com.agronormalizer.model;

import java.time.LocalDate;

public class ApportDto {

    private String numeroApport;
    private LocalDate dateApport;
    private String siteCollecte;
    private String cereale;
    private Double poidsNetKg;
    private Double tauxHumiditePct;
    private String sourceSysteme;

    public ApportDto() {
    }

    public ApportDto(String numeroApport, LocalDate dateApport, String siteCollecte, String cereale,
            Double poidsNetKg, Double tauxHumiditePct, String sourceSysteme) {
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

    public Double getPoidsNetKg() {
        return poidsNetKg;
    }

    public void setPoidsNetKg(Double poidsNetKg) {
        this.poidsNetKg = poidsNetKg;
    }

    public Double getTauxHumiditePct() {
        return tauxHumiditePct;
    }

    public void setTauxHumiditePct(Double tauxHumiditePct) {
        this.tauxHumiditePct = tauxHumiditePct;
    }

    public String getSourceSysteme() {
        return sourceSysteme;
    }

    public void setSourceSysteme(String sourceSysteme) {
        this.sourceSysteme = sourceSysteme;
    }
}
