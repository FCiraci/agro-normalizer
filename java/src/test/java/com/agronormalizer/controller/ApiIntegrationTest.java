package com.agronormalizer.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class ApiIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    private static final String LOT_VALIDE = """
            {
              "numero_lot": "LOT-IT-001",
              "date_pesee": "2026-01-05",
              "poids_carcasse_kg": 300.0,
              "poids_decoupe_kg": 135.0,
              "categorie_classement": "U3",
              "source_balance": "BIZ-01"
            }
            """;

    private static final String LOT_EN_ALERTE = """
            {
              "numero_lot": "LOT-IT-ALERTE",
              "date_pesee": "2026-01-06",
              "poids_carcasse_kg": 300.0,
              "poids_decoupe_kg": 220.0,
              "categorie_classement": "E1",
              "source_balance": "BIZ-02"
            }
            """;

    private static final String APPORT_VALIDE = """
            {
              "numero_apport": "APP-IT-001",
              "date_apport": "2026-02-01",
              "site_collecte": "Silo Nord",
              "cereale": "ble_tendre",
              "poids_net_kg": 1200.5,
              "taux_humidite_pct": 14.2,
              "source_systeme": "ERP"
            }
            """;

    private static final String APPORT_EN_ALERTE = """
            {
              "numero_apport": "APP-IT-ALERTE",
              "date_apport": "2026-02-02",
              "site_collecte": "Silo Est",
              "cereale": "mais",
              "poids_net_kg": 980.0,
              "taux_humidite_pct": 16.0,
              "source_systeme": "WMS"
            }
            """;

    // --- /lots ---

    @Test
    void postLotValideRetourne201EtLObjetCree() throws Exception {
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_VALIDE))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("LOT-IT-001"))
                .andExpect(jsonPath("$.rendement_pct").value(45.0))
                .andExpect(jsonPath("$.alerte").value(false))
                .andExpect(jsonPath("$.lot.numero_lot").value("LOT-IT-001"));
    }

    @Test
    void postLotChampManquantRetourne400() throws Exception {
        String sansPoids = """
                {
                  "numero_lot": "LOT-IT-400",
                  "date_pesee": "2026-01-05",
                  "poids_decoupe_kg": 135.0,
                  "categorie_classement": "U3",
                  "source_balance": "BIZ-01"
                }
                """;
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(sansPoids))
                .andExpect(status().isBadRequest());
    }

    @Test
    void postLotPoidsNegatifRetourne422() throws Exception {
        String poidsNegatif = """
                {
                  "numero_lot": "LOT-IT-422",
                  "date_pesee": "2026-01-05",
                  "poids_carcasse_kg": 300.0,
                  "poids_decoupe_kg": -10.0,
                  "categorie_classement": "U3",
                  "source_balance": "BIZ-01"
                }
                """;
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(poidsNegatif))
                .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void postLotPorcAvecRendementPorcinNestPasEnAlerte() throws Exception {
        // 220/300 = 73,3 % : en alerte pour un bovin (35-60), normal pour un porc (60-85).
        String lotPorc = """
                {
                  "numero_lot": "LOT-IT-PORC",
                  "date_pesee": "2026-01-07",
                  "poids_carcasse_kg": 300.0,
                  "poids_decoupe_kg": 220.0,
                  "categorie_classement": "U3",
                  "source_balance": "BIZ-03",
                  "espece": "porc"
                }
                """;
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(lotPorc))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.alerte").value(false))
                .andExpect(jsonPath("$.lot.espece").value("porc"));

        mockMvc.perform(get("/lots/alertes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void postLotEspeceInconnueRetourne422() throws Exception {
        String especeInconnue = """
                {
                  "numero_lot": "LOT-IT-ESPECE",
                  "date_pesee": "2026-01-07",
                  "poids_carcasse_kg": 300.0,
                  "poids_decoupe_kg": 135.0,
                  "categorie_classement": "U3",
                  "source_balance": "BIZ-03",
                  "espece": "autruche"
                }
                """;
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(especeInconnue))
                .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void getLotExistantRetourne200() throws Exception {
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_VALIDE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/lots/LOT-IT-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.numero_lot").value("LOT-IT-001"));
    }

    @Test
    void getLotInexistantRetourne404() throws Exception {
        mockMvc.perform(get("/lots/LOT-INCONNU"))
                .andExpect(status().isNotFound());
    }

    @Test
    void getAlertesSansAlerteRetourne200EtListeVide() throws Exception {
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_VALIDE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/lots/alertes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void getAlertesAvecAlerteRetourneLaListeFiltree() throws Exception {
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_VALIDE))
                .andExpect(status().isCreated());
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_EN_ALERTE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/lots/alertes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].numero_lot").value("LOT-IT-ALERTE"));
    }

    @Test
    void getListeDesLotsRetourne200() throws Exception {
        mockMvc.perform(post("/lots").contentType(MediaType.APPLICATION_JSON).content(LOT_VALIDE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/lots"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));
    }

    // --- /apports (miroir Silos) ---

    @Test
    void postApportValideRetourne201EtLObjetCree() throws Exception {
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(APPORT_VALIDE))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("APP-IT-001"))
                .andExpect(jsonPath("$.alerte").value(false))
                .andExpect(jsonPath("$.apport.numero_apport").value("APP-IT-001"));
    }

    @Test
    void postApportChampManquantRetourne400() throws Exception {
        String sansSite = """
                {
                  "numero_apport": "APP-IT-400",
                  "date_apport": "2026-02-01",
                  "cereale": "ble_tendre",
                  "poids_net_kg": 1200.5,
                  "taux_humidite_pct": 14.2,
                  "source_systeme": "ERP"
                }
                """;
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(sansSite))
                .andExpect(status().isBadRequest());
    }

    @Test
    void postApportPoidsNegatifRetourne422() throws Exception {
        String poidsNegatif = """
                {
                  "numero_apport": "APP-IT-422",
                  "date_apport": "2026-02-01",
                  "site_collecte": "Silo Nord",
                  "cereale": "ble_tendre",
                  "poids_net_kg": -50.0,
                  "taux_humidite_pct": 14.2,
                  "source_systeme": "ERP"
                }
                """;
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(poidsNegatif))
                .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void getApportExistantRetourne200() throws Exception {
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(APPORT_VALIDE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/apports/APP-IT-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.numero_apport").value("APP-IT-001"));
    }

    @Test
    void getApportInexistantRetourne404() throws Exception {
        mockMvc.perform(get("/apports/APP-INCONNU"))
                .andExpect(status().isNotFound());
    }

    @Test
    void getAlertesApportsSansAlerteRetourne200EtListeVide() throws Exception {
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(APPORT_VALIDE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/apports/alertes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void getAlertesApportsAvecAlerteRetourneLaListeFiltree() throws Exception {
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(APPORT_VALIDE))
                .andExpect(status().isCreated());
        mockMvc.perform(post("/apports").contentType(MediaType.APPLICATION_JSON).content(APPORT_EN_ALERTE))
                .andExpect(status().isCreated());

        mockMvc.perform(get("/apports/alertes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].numero_apport").value("APP-IT-ALERTE"));
    }
}
