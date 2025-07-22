# Analyse Complète : Migration des 18 Fonctions R vers Python

## Résumé Exécutif

Cette analyse détaille les 18 fonctions analytiques critiques du système R-Meta-Analysis d'Aliquanto3/Jiliac et évalue leur migration vers Python. Contrairement à l'analyse précédente qui n'identifiait que 7 fonctions, cette étude approfondie révèle l'ensemble complet des 18 fonctions analytiques avancées qui doivent être migrées pour maintenir la fidélité du système.

**Faisabilité globale :** 75-85% de fidélité possible avec des workarounds appropriés
**Complexité :** Très élevée (5/5) - Significativement plus complexe que la migration C# → Python
**Timeline estimée :** 14-16 semaines pour une migration complète

## 1. Identification des 18 Fonctions Analytiques Critiques

### Groupe 1 : Métriques de Diversité Statistique
1. **Shannon Diversity Index** - Mesure de la diversité du métagame basée sur la théorie de l'information
2. **Simpson Index** - Métrique alternative de diversité axée sur la dominance
3. **Effective Archetype Count** - Mesure pratique de la diversité fonctionnelle
4. **Herfindahl-Hirschman Index** - Mesure de concentration du métagame

### Groupe 2 : Analyse Temporelle
5. **Rising Archetypes** - Identification des tendances croissantes du métagame
6. **Declining Archetypes** - Détection des archétypes perdant en popularité
7. **Volatile Archetypes** - Suivi des modèles de performance inconstants
8. **Stable Archetypes** - Identification des piliers constants du métagame

### Groupe 3 : Intégration Machine Learning
9. **K-means Clustering** - Regroupement des archétypes par caractéristiques de performance
10. **Silhouette Analysis** - Validation de la qualité du clustering
11. **Correlation Matrix** - Analyse des relations statistiques
12. **Significance Testing** - Calcul des p-values pour les corrélations

### Groupe 4 : Analyse des Cartes
13. **Comprehensive Card Statistics** - Analyse de fréquence sur tous les decks
14. **Meta-level Insights** - Tendances et modèles de popularité des cartes
15. **Archetype-specific Usage** - Distribution des cartes par type de deck

### Groupe 5 : Cohérence des Visualisations
16. **Hierarchical Ordering** - Ordre hiérarchique cohérent dans toutes les visualisations
17. **Unified Naming** - Alignement parfait entre les graphiques et la matrice de matchups
18. **Professional Standards** - Cohérence de niveau industriel correspondant aux standards MTGGoldfish

##naux.sateurs fi les utilintielles parpotedifférences des tation cepe et l'ac du prototypultatssur les rés être basée evraithon don R → Pytigrati la mle surion fina
La décis
Manalytics. pipeline  du complète'unificationnt vers lessaut en progres toe les risqu minimisatégieette strritiques. C les plus c fonctionsype sur les protot avec un R → Pythonionigrat la mévaluer, puis aroundsorkoche wl'apprer our validon pC# → Pythigration  par la mcommençantielle, en  séquentrocheapppter une  Ado**le :ion finandat
**Recomma(98-99%).
→ Python ation C# e la migrplexe quus comtement plt netation escette migrà 75-85%, té estimée c une fidélicatifs. Avefis signifiente des démais présle sabuement faichniqon est tethde R vers Pys iqueiques critons analytes 18 fonctin datio

La migrion7. Conclus
##

```sult)py(rei.rpy2s2rurn panda    ret
ipt)(r_data)scrjects.r(r_= roblt esu    r

      """
    )
  clusteringstering =   cluty,
   versisity = didiver  list(

    tsulta résetourner les R    #
)
    ataring(dorm_clusteg <- perf clusterinata)
   diversity(d <- shannon_versityses
    dir les analycute
    # Exé  }
   )
        tte_score
lhoue= si silhouette
       rs,t$centeesuls_r kmeans =   center    luster,
 ans_result$c= kmes ster     clu     list(
 ])
   dth")[, "sil_wi(features)ster, dist_result$clueanse(kmouettilhre <- mean(scoette_sou silh
      = 3)rs, centetures(feaeanst <- kmesulans_r)
      kme")]ateinr", "wa_share("metle(data[, ccaatures <- sfe      ata) {
function(d<- lustering orm_c  perftering
  clusl du  Calcu
    #
))
    }ecks/ total_de_counts hetyp log(arc) *total_deckss / e_countm((archetyp   -su
   e)hetypgth(data$arccks <- lenl_detotape)
      hetyrctable(data$a <- etype_countsrch{
      action(data) ity <- funerson_divhann  siversité
  riques de dl des mét  # Calcu
  ter)
lusbrary(c  litats)
   library(s   ""
 " r_script =   ta)

y(das2ri.py2rpnda= padata   r_ate()
  2ri.activ  pandas
  tiques"""ques cri statistilculsur les ca po""Utilise R  "  data):
_analysis(tatistical
def r_sdas2ri
mport pan2.robjects i
from rpyects robjs as.robjectport rpy2 rpy2
im avecbrideproche hyle d'apon
# Exemp

```pythde R-PythonHybri : ivenathe Alter Approcs)

###maine (0 seop complexe R** si tr **Maintien
  3.nes)8-10 semaiigés (sultats mit si ré**ybridehe h. **Approcnes)
  24-16 semaiconcluant (1ototype i prcomplète** s**Migration *
  1. Options :* mois
- **-4:** Dans 3eline Tim **É 3)
-on (PRIORITPython R →  : Décisi Phase 3s

####elle rénnéesé avec dosabilit fai delidation* Vaultat :***Rés
- itiquescrns les plus iour les fonctototype po un prer Développhe :**Approctiques
- **onctions criur les 18 founds sares worklidation don :** Vaicati- **Justif1
 Phase  mois aprèsDans 1-2ne :**
- **TimeliTÉ 2)n (PRIORI Pythototype R →Proase 2 : )

#### Pheline (70%du piplle ion partieicatniftat :** U
- **Résularoundsroche workon de l'appt, validatiiamédOI iminimal, Rue mn :** Risqtio**Justificas
- 2 semainet - média* Imne :***TimeliORITÉ 1)
- n (PRIC# → Pytho: Migration e 1 asPh
#### tielle
ion Séquendée : Migratcommanche Reppro### A

esgiquatéons Strandati 6. Recommeurs

##isat utilevé pour lesisque él)
- Rnesai4-16 semongue (1- Timeline l notables
visuellesces  Différenr
-es à migre critiquns 18 fonctio)
-75-85%itée (té limidéli- Fnients :**
Inconvé
**e
ermng tà lofiée nance simpli2
- Mainteeps 1-c Stative avetion n
- IntégraRdépendance  de la imination Élpeline
-mplète du pion coficati :**
- Univantages**Athon
tion R → Py#### Migra
isations
alas les visue couvre pnt)
- N Treatmetep 2 (Data à la S
- Limiténts :**nienconvé*I

*emaines)urte (2 seline coim- Teurs
lisatr les utiinimal pou Risque m99%)
-aite (98-i-parfélité quasFid-
ses) (7 clasien définisds bkaroun- Worres (OOP)
imilaigmes s*
- Paraditages :*Avan**n
ytho C# → P Migration####nients

véet InconAvantages #  |

##tiqueCril | Élevé | Minima* | que* |
| **Rises | +600% semain 14-16 |2 semainesmeline** |  **Ti
| à -20% |75-85% | -158-99% | lité** | 9 **Fidéles |
|es visuelrencée | Diffé| Spécialis Simple lisation** |Visuaevée |
| **élxité es | Complees nativcéaniques | Avues** | BasStatistiq
| **plète |e com | Réécriturntere diffé| Très| Similaire *Syntaxe** ental |
| *ndamt foangemenl → OOP | Chnenction| Fo OOP → OOP * |Paradigme*| **--|
--------------|------|--------------
|--------|-nce || Différeython  R → P→ Python |C# | Aspect | s

eureférences Majif## DPython

#ration C# → son avec Migaipar

## 5. Com`ax
``eturn fig,   r
    ut()
      ght_layo     plt.tiion=0)
   rotatlt.yticks( p
       a='right')on=45, hs(rotati plt.xtick
       'bold')tweight==14, fontsizetitle, fone(itl_t.set
        axntique à R # Style ide
       )
               ax=ax        ate'},
    : 'Win Rkws={'label' cbar_
         f',   fmt='.2                t=True,
nno a                 .5,
 =0      center
       dBu_r',='R  cmap
     tmap(data,   sns.hea)
      =(12, 10)zeplots(figsiub.s pltfig, ax =        c style R
veap aa heatm Créer l
        #     ault')
   use('deft.style.pl    yle R
     le sturer# Config

      )archetypeschy(es_by_hieraretyprchity.sort_aibilmpatationCoaliz RVisu =rchetypes sorted_a)
       .unique(etype_col][archpes = data     archety   nte
ohéree cèrmanie  les trier dchétypes etes ar la liste d Obtenir      #

  (data)columne_hetyp_arc.getpatibilityzationCom = RVisualitype_col      archechétype
  d'arne a colonenir lpour obttralisée cenn fonctioiser la   # Util      """
lysis-Ana de R-Metaaptm heat laeprodui"R    ""x"):
    atrihup M"Matc title=ata,(dheatmapte_  def generaod
  staticmeth
    @hetype"
n "arc   returors"
     pe_with_coln "archetyretur
      f.columns:in d" _with_colorstype  if "arche     ponible
 ors' si disth_coltype_wiférer 'arche  # Pré""
      nalysis"e R-Meta-A dumn()olrchetype_cget_aroduit  """Rep
       f):olumn(d_archetype_cget   def od
 methatic
    @sthetypes
 ed_arcorteturn s
        r        aining))
ted(remor.extend(schetypes  sorted_ars]
      etypeted_archn sorot ia netypes if rcha in a [a for ining =   remae
     bétique alphar ordrrchétypes pales autres aajouter e   # Ensuit
           ty)
 (priori.appendrchetypes_arted so          :
     archetypesriority in  p       ifypes:
     archetn priority_iority ifor pr
        t présentss sontaires s'ilioris prhétypeles arcrd ajouter      # D'abo
    = []
 ypesetsorted_arch
  quementhabétiité puis alpar priorier p     # Tr
   "]
      dos Midrangeak", "Rtrolr Con "Dimiowess",et Pres = ["Izzty_archetyp     prioris
   étypens archtaicerle pour ité spéciaior Pr
        #is"""eta-Analyschy() de R-Mby_hierares_t_archetypt sorodui"Repr     "":
   types)rcheierarchy(a_hhetypes_by_arc   def sorthod
   @staticmet"

  ation R""lissuations de vi les foncoduitpr   """Rety:
 patibiliizationComRVisualass clpython


```sation Rsualiibilité ViCompatround 4 : # Worka##


```  }ions
      rrelatongest_co strions':st_correlat    'stronge
        ce_tests,gnifican': siance_testsfic  'signi
     ion_matrix,': correlation_matrixelat     'corr{
       eturn        r
 rse=True)
eve      r                            ]),
     correlation'abs(x['lambda x:   key=                                 s,
    relationtrongest_corrted(sations = sorelgest_cortron   s
      comme R Trier        #
)
             }
     ue < 0.05ant': p_valnific       'sig               4),
   lue,_vand(p': roualuep_v  '
        value, 4),d(corr_on': rounrelati        'cor                : col2,
2'ble    'varia                 l1,
   ble1': coaria'v                  {
      pend(ions.apelatcorrrongest_        st
                a())
 pncol2].drota[), dana(rop].d(data[col1rsonrea = stats.pueval    stat, p_        :
        .all()a()snl2].iot data[co) and nisna().all(ata[col1]. not d        if     test()
   cor.mme R ation co de corrél  # Test
                  i, j]
  rix.iloc[n_matcorrelatioe =   corr_valu
    _cols[j] = numeric  col2
         ic_cols[i]l1 = numer      co         ls)):
 _coric 1, len(numee(i +r j in rang   fo         ):
ic_cols)e(len(numerangi in r   for ]
     ns = [_correlatiorongest st
       mme Rfortes cos les plus tionélas corr# Trouver le
                   }
      5
      e > 0.0l': p_valus_norma   'i             , 4),
    (p_value': round 'p_value             ),
      nd(stat, 4istic': rou 'stat
   {lity"] =col}_norma"{ests[fe_ticanc      signif
  pna())[col].drotahapiro(dae = stats.salu, p_v       stat        e R
 ilk commShapiro-Wité t de normal       # Tes         :
.columnsdata in  colif        _cols:
    mericor col in nu
        fests = {}gnificance_t    si    e R
té commificativis de sign    # Test
  rson')
   (method='peaorrmeric_data.c= nun_matrix latioorre   c     me R
ise comhode pairwavec méton atiélrice de corrr la mat Calcule   #
     s]
       oleric_c[numata= data meric_d       nus
 mner]).colup.numb[nlude=t_dtypes(inca.selec datc_cols =meri   nu      R
riques commennes numéloner les coion   # Sélect    ""
 ysis"a-Anale R-Metion dorrélats de c les testit"Reprodu  ""      ons(data):
elatiorr_cateul    def calcthod
metic  @sta
      }

  tatsype_s: archetats'hetype_st 'arc       ,
    te_scoreouetilh': se_scoresilhouett         's_,
   r_centerste.clus': kmeanstercen 'cluster_          ,
 )), clusterstures.indext(zip(feausters': dicpe_clchety  'ar      rn {
           retu
 e 0
     )) > 1 elssterst(clu len(sesters) ifta, clualed_da_score(scettehoucs.siltrie_score = mesilhouett      R
  te comme re silhouet le sco# Calculer
      d_data)
   redict(scalekmeans.fit_pclusters = 0)
        t=1=42, n_inim_stateandosters, r_clu=n_clustersns(n KMeakmeans = R
        e àquseed identiavec ans  k-melusteringe cfectuer l   # Ef
     )
       turessform(feait_tran.fta = scaler scaled_da
       aler()Sc= Standard   scaler
cale()comme R ss features er leardisand    # St

        (0)fillnainrate']].', 'wre[['meta_shae_statstypchearres =      featu  tering
 r le clusouonnées per les d# Prépar
               ta)
 dan(count'] / leats['deck_strchetype_hare'] = a['meta_statshetype_s     arc
   t'}))
  : 'deck_counhetype''arcs={olumn   .rename(c                   n'})
     e': 'mea'winrat                              'sum',
    'losses':                          ,
       : 'sum'ns'wi '                              ,
  unt'e': 'cotypchearagg({'    .                       ype')
etoupby('arch(data.grats = stpe_archetys
        étypechnce des arformas de pers métrique Calculer le #
       "ysis""R-Meta-AnalK-means de tering le clusoduit pr   """Re:
     clusters=3) n_ng(data,riorm_cluste    def perficmethod
@stat

   ning R""" learineions de mach foncteproduit les"R  ""ity:
  ompatibil RMLCsshon
cla``pyt

` Ringachine Learntibilité Mmpa3 : Coound ## Workar``

#rends
` return t
latile'
   gory'] = 'Vo> 0.1, 'cate] lity''volatis[ndnds.loc[trere     tlining'
    'Dec] =ory'2, 'categ < -0.0rend']a_share_t'metloc[trends[     trends.ising'
   = 'Rory'] .02, 'categ_trend'] > 0'meta_shareds[trenoc[trends.l
    'le= 'Stab'] s['category     trend
   cesles tendanr # Catégorise
    })))
                      0)
se) > 1 elf len(x i(x), 1) / max(len
  iloc[0]) are'].'meta_shx[c[-1] - .iloa_share']['met: ((xe'wth_rat        'gro           .std(),
   eta_share']ility': x['m   'volat              ,
     n()eaf().m].difmeta_share'['trend': xshare_  'meta_                an(),
    ].me_share'['metaare': xeta_shavg_m         '            en(x),
 _present': l   'periods                   s({
pd.Serie x: pply(lambda.a
     e')('archetypupby.grol_datatempora = (  trends
      archétypear  pdancesles ten Calculer        #

        ('sum')].transformount'k_c['deciod')er'poupby(l_data.gr/ tempora'] 'deck_countta[temporal_da_share'] = ['metatadamporal_
        te périodeméta parart de la pculer  Cal      #
     '}))
  unte': 'deck_co'archetypns={e(colum   .renam                    '})
  te': 'mean    'winra                         sum',
   'losses': '                             m',
 su 'ns':      'wi                      ,
   e': 'count'{'archetyp     .agg(                 pe'])
   tyiod', 'archeupby(['perdata.gro = (tamporal_da  te
  ')
     iod('Wper.to_t_date']).dtmena['tourname(datatetio_dd'] = pd.tdata['perio        rchétype
t aiode e par pérrouper        # G"
s""Meta-Analyside R-trends() ral_mpot analyze_te""Reprodui       "s(data):
 poral_trendyze_temanal
    def staticmethod
    @  R"""
  relle se tempod'analyns tioit les fonc""Reprodu
    "ility:oralCompatibass RTempn
cl```pytholle R

mporenalyse Teité Aompatibil : CWorkaround 2

### )
```untschetype_coarin or count  ** 2 fdecks)al_/ totunt ((coreturn sum)
        en(data= ll_decks        tota
 ue_counts()alrchetype'].v = data['aype_counts    archet"""
    a-Analysiset de R-Mx()_indedahlt herfineprodui""R"    ata):
    (dexndahl_ind   def herfimethod
 @static
    )
   p(shannonnp.exreturn a)
        dat_diversity(nnonty.shapatibilisComStathannon = R"
        ssis""ta-Analy R-Me dees()chetyp_arit effective"Reprodu     ""):
   types(datave_archeeffecti    def ticmethod
sta    @s)

ountype_cett in archfor coundecks) ** 2 otal_((count / tum1 - s return
 ta)cks = len(datal_de        toounts()
e'].value_carchetyp = data['etype_counts arch""
       sis"-Meta-Analyde Riversity() _dpsoneproduit sim"""R      ta):
  ty(daersin_div  def simpso
  d@staticmetho
counts)
  e_ in archetyp count    for            )
    ecks / total_duntlog(codecks) * np. / total_untum((co  return -s  a)
     len(dat =l_decks      totats()
  counlue_'].vape'archety = data[tsetype_coun      arch"
  nalysis""ta-Ay() de R-Men_diversitshannooduit Repr  """
 (data):sity_divernnonha def sethod
   icm
    @stat"
   "" R critiquestistiquestaonctions sit les feprodu """R
   ibility:StatsCompathon
class R``pyt R

`tistiqueté Staatibiliompound 1 : C### Workarète

omplation CMigr pour  Nécessairesorkarounds## 4. W: 75-85%

 estimée** ité globaleFidélvée)

**88% (Éle** : 80-ationsualisence VisCohér5. **vée)
5-90% (Éle** : 8rteses Case d
4. **Analyée)Élev(Moyenne-72-82% ** : ning Learneachi **Me)
3.5% (Élevé-8le** : 80se Temporel
2. **Analyès élevée)5-98% (Trrsité** : 9s de Diveueriq*Mét1. *nctions

pe de Fopar Grouyenne  Fidélité Mo###

 | Élevérès élevée |65-75% | T| rn seabo matplotlib/andards |nal Stfessio| Pro18 |
| | Faible aible 5% | F90-9as | andaming | pied Nif| 17 | Un |
 | Faibleble5% | Fai-9 sort | 90on | pythOrderingical  | Hierarch| 16 Moyen |
 | Moyenne |as | 85-90% | pandgeUsapecific chetype-s
| 15 | Aryen |ne | Mo | Moyen90%andas | 85-sights | pta-level In | Me|
| 14yen  | Mone90% | Moyen 85-andas || ptistics Card Sta| evé |
| 13 e | Éllevé80% | És | 70-y.stating | scipicance Testnif12 | Sigé |
| | Éleve enn0-80% | Moycorr | 7 | pandas.atrix MCorrelation1 | | 1 |
vé | Éle85% | Élevée5-.metrics | 7earn| sklysis Analhouette
| 10 | Sil Élevé |ée |5-85% | Élevcluster | 7g | sklearn.terinans ClusK-me
| 9 | oyen | M | Moyenne |das | 80-85%panpes | chety| Stable Ar| 8 Moyen |
| Moyenne | % ndas | 80-85s | patypeile Arche | Volaten |
| 7| Moynne oye5% | Ms | 80-8| pandaypes chetDeclining Ar 6 |
|oyen |yenne | M | Mo85% 80-pandas |rchetypes |  A Rising
| 5 |Faible | | ble% | Fai98| 95- numpy x |an Indehl-Hirschmda| Herfinble |
| 4 | Faie  | Faibl8%-9y.exp | 95 | numpype Countrchet Effective A 3 |Faible |
|le | aib| 95-98% | Fy dex | nump InSimpson
| 2 |  | Faible |98% | Faiblepy | 95- num | scipy +sity Indexveron Di Shann| 1 ||--------|
-----------------|---------|---------|-------------|-------ue |
|- Risqté |Complexié | on | Fidélitvalent Pyth | Équi| Fonction R

| #  Fonctionsif des 18eau Comparat Tabl

### GlobaleomparativeAnalyse C
## 3. .
nt en Pythonmeidèleduites fêtre reproent et peuvimples lativement s sont recolonnesction de et de séle tri ons de
Les foncti : 90-95% Fidélité

#### }
```
 _coltype: archemn'colue_yp   'archets,
     pehetyd_arc sortechetypes':ed_ar       'sortreturn {


    ations ici)e visualisnération dde gé    # (code érent
l'ordre cohions avec lisatvisuaer les énér
    # G
s)(archetypearchy_hierhetypes_byrt_arc sopes =etysorted_arch   ique()
 pe_col].un[archetyatahetypes = d arcrente
   ohé c manièreier de tr et leschétypesdes arr la liste nite
    # Ob
    a)atlumn(de_coetypget_archetype_col = pe
    archarchéty d'nnecolo la r obtenirtralisée poution cen foncliser la"
    # Utiis""eta-Analysde R-Mations lis visua desde cohérenceème t le systReprodui    """ns(data):
sualizatiot_viensistate_conerf gende"

chetypeurn "ar
    retors"with_coletype_turn "arch
        reolumns:s" in df.cith_colore_whetyp "arcif   ible
 s' si disponwith_colorhetype_r 'arc Préfére #
   ype"""archéte colonne d'lection de de séalisénction centrfoproduit la ""Re
    "n(df):ume_colarchetypet_

def getypessorted_archrn  retu

))ininged(rematend(sortes.exed_archetyp
    sortetypes]orted_archf a not in spes ihetyarcor a in [a fmaining = ue
    retiqhabé ordre alpypes pars archétr les autreoutete aj    # Ensui
ority)
ppend(prietypes.achted_ar         sores:
   in archetypf priority       ietypes:
  ity_archior in prorityor pri    f
nts sont présetaires s'ilss prioriétyper les archd ajoute D'abor
    # = []
    archetypes  sorted_ement
  bétiqulphauis ariorité prier par p T #
   ]
   s Midrange""Rakdo r Control","Dimi,  Prowess"= ["Izzethetypes arc priority_pes
   ns archétyaiour certle porité spécia# Pri"""
    nalysisde R-Meta-Aypes éte des archhiquhiérarctème de tri  le sysoduit"""Repres):
    y(archetyp_by_hierarch_archetypesdef sortython
hon
```pt Pytenquival``

#### É  ))
}
`ype_col
rchet_column = ahetypercpes,
    ahetyd_arc= sorteypes ed_archett(
    sorturn(lis
  ret
   ici)lisationssuaon de vi génératide de
  # (coente cohérl'ordrc isations avesuales vinérer lGé

  # pes)(archetyrarchyietypes_by_hort_arche setypes <-archted_ol]])
  sorpe_chety(data[[arcique <- unypes
  archethérentemanière co de et les trierrchétypes es ae dlista ir l # Obten

 (data)umntype_colt_archeol <- gepe_crchety  aétype
onne d'archla colenir our obtisée pralion centla fonctliser {
  # Utidata) function(ions <- izatualent_vise_consistratene
}

getype")"archeturn(}
  r  lors")
cope_with_n("archetyur{
    retes(df)) amcoln%in% h_colors" etype_wit("archnible
  if pos' si dislor_with_coarchetyperéférer '# Pn(df) {
  iomn <- functolu_archetype_c}

get(sorted)
 return
 g))
  ainin(remorted, sort<- c(s)
  sorted edypes, sortf(archet <- setdifmaininge
  realphabétiqu ordre es parres archétyples autte ajouter   # Ensui}
  }


    ority)ed, prirtd <- c(so   sorte
    {etypes)chty %in% arif (priori{
    hetypes) rc_apriorityty in (priorior résents
  f sont p'ilsres s prioritaiarchétypes les jouterbord a

  # D'a c()ted <-ent
  sorhabétiquemis alprité purio p # Trier par

 ") MidrangedosRak", "ontrol"Dimir Css", Prowezet  c("Iz<-es archetyprity_s
  priorchétypecertains aiale pour rité spéc  # Prioes) {
etypch(arnctionchy <- furarhies_by_rt_archetypes
soation visualishérence dese costème dnalysis - Sy-AMeta`r
# R-
`` R Original
#### Codeisations
alsuence des Vihér : Conction 16-18
### Foles.
fidèralement s sont géné statistiquecalculs mais les et Python, R nte entreféregèrement dife lé peut êtrs imbriquéesnéeres de dontustruculation des
La manipé : 85-90%#### Fidélit
`
  }
``  cribe()
_rate'].dests['usageard_stabution': cage_distri        'us_usage,
chetype_card: arsage'archetype_u
        'top_cards,cards':        'top_ats),
 len(card_stds': ique_carotal_un   't
     eturn { r

             }))                 ': 'mean'
 nrate  'wi                             mean'],
m', 'suntity': ['     'qua                    g({
              .ag                   e'])
card_namype', 'rchetby(['af.group(cards_dard_usage = hetype_c
    archétype par arc Cartes

    #e_rate')ag'ust(20, es.nlargtss = card_stard
    top_cailisation par utop cartes    # T
  a)
 (datunt'] / lenrchetype_cotats['ard_s'] = caratege_d_stats['usa]
    carats.columnsard_st col in c(col) for_'.join['lumns = .cots_sta    card}))

                 n'
 'meae':    'winrat             ue'],
    iqnun', 'e': ['countarchetyp      '
       an'],, 'me: ['sum'ity'quant       '                .agg({
      )
         card_name'by('df.groupards_s = (c  card_stattes
  es carlobales dues gtatistiq
    # S)
    me(all_cards pd.DataFracards_df =me
     en DataFra Convertir
    #urn {}
 et     rards:
   _ct allnof
    i
      })
          ']nratew['wie': rorat       'win              type'],
   arche row['pe':hety 'arc              ,
         ', 1)t('Quantity.gentity': card       'qua            me'],
     Naame': card['  'card_n
   .append({ all_cards
         card:ame' in ict) and 'Nnce(card, d if isinsta                cards:
r card in       fo
     st):rds, licaisinstance( if
       ', [])'deck_cardsrow.get(ds = ar    c):
    errows( data.itx, row in   for id[]
 _cards =
    all les decks de tousartesles coutes traire t
    # Ex{}
       return
 a.columns:ot in dateck_cards' nif 'd""
    "alysis-AntaR-Mees de des cartse lynauit l'aeprod"R:
    ""usage(data)d_carnalyze_def an
ho
```pythonnt Pytquivale
#### É
```

}
  ))rate)ge_stats$usa(card_ryn = summautiodistrib   usage_ge,
 ard_usachetype_c = ar_usage  archetypeards,
  top_c_cards =
    topd_stats),ow(car_cards = nrque   total_uniurn(list(


  ret)
    )nrateean(wirate = m  avg_winty),
    antiy = mean(quantitvg_qu  atity),
     = sum(quanantity  total_quarise(
      summ) %>%
  me card_nahetype,roup_by(arc %>%
    grds_dfsage <- cape_card_uarchetychétype
   ars parrte
  # Ca20)
     head(%>%
te)) sage_raange(desc(u    arrs %>%
statd_ car_cards <-ion
  topsat par utiliTop cartes

  # ow(data)nrt / counts$deck_ard_sta<- cate ats$usage_r card_stn
 satiod'utili le taux uler
  # Calce)
    )
  mean(winratate =vg_winr
      ae),yparchetn_distinct(_count = ype  archet,
    ()ount = n deck_c     y),
quantity = mean(vg_quantit    atity),
  = sum(quanl_quantity  totaise(
     ummar
    s>%name) %up_by(card_ro g  >%
 s_df %card- rd_stats < caes cartes
 s ds globaletatistique Se))

  #fram.data.s, as(all_cardnd, lapplyll(rbicas_df <- do.ard  cframe
ir en data vert
  # Con}
ist())
   return(l{
   = 0) ll_cards) =(length(a
  if .null)]
 s, isly(all_cardcards[!sapps <- all_all_cardl_cards)
   al.call(c, <- doall_cardses
  artste de cir la li Aplat
  #)

  }}))

      te deck$winra winrate =
       hetype,arctype = deck$       archentity,
 rd$Qua= caity   quantme,
      me = card$Nana  card_
      (    listcard) {
  function(, (cards  lapply


    }turn(NULL)  re 0) {
    ==th(cards) eng lll(cards) ||nu(is.
    if ards
 ck_cck$de cards <- de   ata[i, ]
 <- d  deck{
  n(i) ionctta), furow(daapply(1:nl_cards <- l
  als les decksartes de tous c leraire toutes) {
  # Extdataion(ctun fsage <-ard_uanalyze_cs cartes
 Analyse delysis --AnaMetaR-
```r
# e R Original
#### Cods Cartes
nalyse den 13-15 : Actio

### Fonrésultats.ffecter les  aentemt égaltes peu manquanvaleursion des on. La gestélatirrde cot les tests o-Wilk) elité (Shapirde normas testnt pour les ticulièremes, part différent légèremensultatss réuire depeuvent prodon et Pythques en R tistitests sta80%
Les  70- :Fidélité### }
```

#
 rrelationsst_co': strongeelationsrrco 'strongest_  sts,
     icance_tes': significance_test 'signif    atrix,
   relation_m': coron_matrixelati 'corr        {
rn    retu

=True)everse   r
 tion']),orrelax: abs(x['cmbda    key=la                              tions,
  elarrstrongest_cod( = sortecorrelationsest_ngtro slation
   ue de corréeur absoler par valri
    # T    })
       5
        < 0.0e valu p_':cant 'signifi
  lue, 4),round(p_va'p_value':                    4),
  (corr_value,roundon': relati     'cor               2': col2,
variable   '                 1,
: colriable1'   'va                .append({
 elations_corr  strongest

     dropna())l2].cota[daropna(), 1].dol[crsonr(datas.peavalue = stat, p_    stat           ).all():
 ].isna(data[col2t and noall() l1].isna().t data[co if no
  ioncorrélate est d      # T

       iloc[i, j]on_matrix.relati cor =_value        corr
    [j]cols2 = numeric_    col   [i]
     umeric_cols n    col1 =  ):
      cols)numeric_(i + 1, len(gefor j in ran       ):
 _cols)(numericnge(len raor i in fns = []
   elatiocorr  strongest_rtes
   les plus foorrélationss couver le  # Tr
        }
   0.05
    ': p_value >is_normal        '
        e, 4),p_valund(: rou'p_value'              at, 4),
  ound(stc': r  'statisti           {
    y"] =_normalit"{col}[festsnificance_t      sig))
      pna([col].droatahapiro(dstats.slue = stat, p_va
  normalitét de       # Tesmns:
      data.colu   if col in  _cols:
   l in numeric  for co
  e_tests = {}gnificanc
    sificativitéts de signi # Tes

 ta.corr() numeric_da_matrix =elationorr c
   tionde corrélamatrice alculer la    # C]

 c_cols data[numeric_data =
    numerir]).columnsde=[np.numbetypes(inclulect_d= data.secols    numeric_
 queséries numnns coloner lection    # Sélesis"""
eta-Analyivité de R-Mgnificats de si les testation etce de corrélla matrieproduit    """R:
 ons(data)latite_corre calculaefhon
dthon
```pyt Pyquivalent### É
#`

`` ))
}ions
 relattrongest_corlations = srretrongest_co    sts,
cance_tesnifists = sigificance_te  signtrix,
  relation_maatrix = correlation_m cor(list(
     return)]

 TRUE =ingcreason)), de$correlatis(x(x) abtionuncs, fationst_correlply(strongeer(sapations[ordorrel strongest_crelations <-trongest_cor
  sorrélationabsolue de c valeur  Trier par
  # }

 )
    }5
      alue < 0.0or_test$p.v= cgnificant    siue,
     r_test$p.val co  p_value =  value,
    = corr_correlation
 col2,iable2 =   var      = col1,
 e1  variablist(
      + 1]] <- ltions) st_correlangth(strongetions[[leelarrst_costronge     )

 ata[[col2]]eric_d]], numcol1data[[meric_or.test(nu <- c cor_test   tion
  laréde corest      # T
 [i, j]
   matrixion_correlatrr_value <-
      coix)[j]ion_matr(correlatlnames<- co      col2 trix)[i]
lation_maorrecolnames(cl1 <-       coatrix)) {
_mrrelationconcol((i + 1):for (j in  1)) {
    x) -atrielation_ml(corr(i in 1:(nco
  for  <- list()ationsorrelgest_cron stortes
  les plus ftionscorrélaer les   # Trouv  }

05
    )
 0.lue >_test$p.va shapiroormal =     is_n$p.value,
 hapiro_test p_value = sstic,
     t$statitesapiro_istic = shstat      - list(
ality")]] <orm_nol, "aste0(cce_tests[[pansignific
  )_data[[col]]est(numeric.trost <- shapiteo_shapiralité
    t de norm   # Tesa)) {
 ic_datumeres(n in colnam  for (colist()
s <- l_testgnificanceivité
  si significat# Tests de

  )obs"lete.comprwise. = "paiuse_data, r(numericco <- rixon_mattin
  correlaorrélatioatrice de c mlculer la
  # Cacols]
  ic_mer, nu<- data[ata eric_d
  numeric)um, is.n sapply(dataeric_cols <- numiques
 mérs nu les colonnenner# Sélectio{
  ion(data) uncttions <- frelate_corité
calculaive significattests dn et rrélatioice de coysis - Matr-Meta-Anall
```r
# Rrigina Code R O####g

nce Testinet Significax tion MatriCorrela1-12 : on 1# Foncti##.

tteuescores silhodes ul e calct loïdes eentrion des c'initialisat pour lementièr, particult-learns R et scikiancifiques dtions spéntalémeson des imps en rairentrement diffésultats légèire des révent produring peuclustee rithmes d5%
Les algo : 75-8élité

#### Fid``  }
`_stats
  chetype_stats': ar'archetype     ore,
   ilhouette_scscore': ssilhouette_        'centers_,
luster_ans.cs': kmenterr_ce'cluste       rs)),
 dex, clusteinatures.ct(zip(fe diers':pe_clusthety    'arcn {
       retur
 se 0
   el> 1 )) rsclusteet(len(s) if a, clustersdate(scaled_te_scoruetcs.silhoe = metriouette_scor
    silhouettescore silhculer le al # C
   lusters
  = cluster'] ats['crchetype_st  atype
  archéues d' statistiqr aux de clustelabelsAjouter les #

    aled_data)dict(scfit_pres.= kmeansters 2)
    clute=4andom_staers, rluststers=n_cKMeans(n_clueans =    km k-means
 clusteringe ffectuer l
    # Eres)
 (featurmfit_transfoler.= scaata _d   scaled
 er()alrdScler = Standares
    scaer les featu# Standardis

(0)na']].fill 'winratehare',ta_s['me_stats[ypes = archeture
    featsteringclule nnées pour r les do  # Prépare
en(data)
_count'] / ldeck['tspe_sta] = archetya_share'ts['metsta archetype_)

   ount'}) 'deck_crchetype':s={'ame(column .rena
      n'})'mea'winrate':                             : 'sum',
  'losses'
     'sum',   'wins':
        nt', 'cou'archetype':  .agg({               pe')
      hetyby('arcata.grouptats = (de_s   archetyppes
 s archétyormance dede perftriques ler les mé  # Calcu
  lysis"""naR-Meta-Ahouette de alyse sileans et l'an-mustering Kit le cl""Reprodu"s=3):
    usterdata, n_cling(terclusm_archetype_def perfor``python
hon
`Pytquivalent ## É
```

##
} ))ts
 type_stahearcts = pe_sta
    archetytte_score,ilhoue = ste_score    silhouet,
lt$centerssu_res = kmeanserster_cent),
    clufeatures)mes(ster, rownaclueans_result$ames(km setNusters =chetype_cl  ar
  urn(list(

  retdth"])[, "sil_wi))eaturesdist(fuster, _result$clnsuette(kmeasilho <- mean(rette_scosilhoue)
  ustercl  library(uette
lhoore sir le scculeCal # r

 sult$clusteeans_reter <- kms$clusstatpe_e
  archetychétypd'arues tatistiqr aux se cluste labels douter les
  # Ajters)
  = n_cluss centerres, eans(featuesult <- km
  kmeans_rseed(42)t.
  seg k-meansterinlusectuer le c Eff
  #e()
    scalte) %>%
 share, winraeta_   select(m%
 ype_stats %>rchetres <- a featu
 eringuste clées pour lr les donnrépare P
  #
    )
   nrow(data) /share = n()  meta_,
    rate) mean(winate =     winrs),
 osseum(l = s     losses(wins),
 ns = sum    win(),
  eck_count =      dse(
 mari   sum>%
 pe) %rchetygroup_by(a>%
    - data %s <chetype_states
  ares archétypmance d performétriques deler les  # Calcu3) {
 lusters = n(data, n_c<- functio_clustering etypechperform_arouette
lhyse si anal-means etng K - ClusterisisAnalyr
# R-Meta-``
`riginal R OCode## lysis

##Ana Silhouette lustering etK-means Cion 9-10 : ### Fonctilité.

lates et de vondancculs de teour les calrement pculiètats, partirésulns dans les es variatior dusepeuvent caet pandas re R orelles ent séries tempn desio la gestérences danses diff: 80-85%
Ldélité
#### Fids
```
 trenreturn

    tile'= 'Volary'] 1, 'categoy'] > 0.itnds['volatil.loc[treends   tr
 lining''] = 'Dec, 'category < -0.02end']eta_share_tr['mndsds.loc[treening'
    tr'Risry'] =  'catego > 0.02,rend']hare_tds['meta_strenrends.loc[e'
    ttablry'] = 'Snds['categos
    trece les tendanatégoriser    # C
  )))
          }  0)
   x) > 1 else , 1) if len(len(x)     / max(
   ) ].iloc[0]share' - x['meta_oc[-1]a_share'].ilx['meth_rate': ((growt '
        e'].std(),x['meta_sharlatility': 'vo                 ,
 ().mean()e'].diff['meta_shar xtrend':hare_eta_s   'm            n(),
   hare'].meaeta_s': x['mre_meta_shavg  'a              (x),
  : lenods_present'     'peri        es({
     a x: pd.Seri(lambd  .apply        type')
    rcheupby('ata.groral_dapoends = (tem
    trypehétarcnces par nda les teCalculer
    #     m('sum')
'].transfornt)['deck_cou('period'roupbyl_data.g] / tempora_count'ata['deckal_dempor'] = tharedata['meta_soral_ tempiode
   a par pérétla part de mlculer
    # Ca    count'}))
pe': 'deck_rchetyolumns={'aame(c       .ren          )
    ': 'mean'}ate       'winr                    'sum',
'losses':                           m',
 ins': 'su'w
     : 'count',etype'.agg({'arch
 type'])d', 'archeperioupby(['a.grota = (datal_dapore
    temchétypet ariode pérr par roupe G"
    #"sis"ly-Ana R-Metas derelleances tempotende des ysl'anal"Reproduit     ""ta):
nds(daral_trelyze_tempo
def ana
```pythonlent Python### Équiva

#ds)
}
```eturn(tren

  rVolatile"" > 0.1] <- $volatilityegory[trendsnds$cat
  trelining"<- "Decd < -0.02] enta_share_trs$merend[toryds$categ"
  tren- "Rising <> 0.02]trend $meta_share_egory[trendscat  trends$able"
 <- "Stds$categoryes
  trens tendanciser leatégor C #
  )
  / n()
   e)) sharirst(meta_are) - fast(meta_she = (lh_rat      growthare),
= sd(meta_s volatility e)),
     f(meta_sharifd = mean(d_share_tren
      metae),_sharmean(meta= re ta_sha  avg_me,
    nt = n()riods_prese
      pemarise(  sumpe) %>%
  by(archetyup_%
    groa %>mporal_dat <- te
  trendsrchétypear aes ptendanculer les  # Calcunt))

 k_co sum(decnt /coudeck_are = _shtate(meta
    muod) %>%_by(perigroupta %>%
    al_daemporta <- t temporal_daode
 ta par péri mé dea partlculer l  # Ca
)
    )
  inrate = mean(w   winrate   losses),
 sum(ses =    los,
   = sum(wins)ns     wi,
 ()= nount  deck_ce(
      summaris %>%
   type)rche aperiod,   group_by(a %>%
 datl_data <- temporaype
  t archétpériode epar rouper a) {
  # G(datunctionrends <- fl_tmporae_tealyzporelles
anes temance des tendnalysysis - AMeta-Anal```r
# R-
 Original
#### Code Rs
s Temporelles Tendancelyse de8 : Anaion 5-nct
### Foée.
ev éldélité très fivecque direct aul mathémati5-98%
CalcFidélité : 9

####
```unts)_cotypent in arche 2 for cou **decks) / total_unturn sum((co ret

   ) = len(dataal_decks totnts()
   _coutype'].valueta['archets = daetype_coun    archysis"""
Analeta-x de R-Mden Inschma-HirHerfindahlnction oduit la foepr
    """Rex(data):ndahl_ind
def herfipythonhon
```uivalent Pyt

#### Éq)
}
```tal_decks)^2 / toype_countset((arch  sum)

$archetype(datagthlencks <- detal_  totype)
data$archetable(e_counts <-   archetypdata) {
ction( <- fun_indexfindahlrschman
herl-Hiindahice Herfsis - IndAnalyta-
# R-Meginal
```r R Ori
#### Codex
IndeHirschman l-indahrfction 4 : He.

### Fon très précisementnérals géaiy, m Diversit de Shannonfidéliténd de la -98%
Dépeté : 95li Fidé```

####p(shannon)
eturn np.ex
    r)sity(datavernon_dishanshannon = """
    sisAnaly R-Meta-ount derchetype Cive AEffecttion  foncuit laod""Repr
    "ta):es(daive_archetypfectdef efon

```pythhonuivalent Pyt# Éq

###```}
on)
shannta)
  exp(diversity(da<- shannon_
  shannon a) {n(dat functios <-pe_archety
effectiveeshétyptif d'arcombre effecAnalysis - Nr
# R-Meta-riginal
```## Code R Ount

##rchetype CoEffective Aonction 3 :
### Fs élevée.
té trèli avec fidéue directmathématiqlcul 8%
Caté : 95-9déli

#### Fi``
`nts)e_couetypount in arch 2 for cl_decks) **count / tota sum(( return 1 -)

   (data len = total_decks)
   ounts(.value_cpe']rchetya['adate_counts =    archetyp""
 is"a-Analysty de R-Metson DiversimpSila fonction "Reproduit ""ata):
    diversity(df simpson_
de
```pythont Pythonalen### Équiv

#)^2)
}
```total_decks_counts / (archetype 1 - sum(ype)

 etdata$archgth(<- len_decks
  totalhetype)le(data$arcunts <- tab_co
  archetypedata) {n(- functioity <rs_dive
simpsonde Simpson Indice ysis -eta-Anal
# R-M
```r R Originalde

#### Coson Index 2 : Simp### Fonction

rs nulles.on des valeuestis dans la gntielleneures poteférences mi dif desques, avecdenti sont ihématiqueslculs mat
Les ca5-98%élité : 9# Fid

###ts)
```hetype_counount in arc    for c            _decks)
totalnt / * np.log(couecks) al_dtot/ m((count n -suretur
    en(data)
 ks = ll_dec  tota  counts()
'].value_peta['archety= das _count  archetype"
  sis""Meta-Analyde R-n Diversity  Shannola fonctionroduit   """Repta):
  ersity(da_divannonshthon
def pyython
```t P# Équivalen
###}
```
al_decks))
counts / totetype_char) * log(cks_de / totalcounts((archetype_sum

  -type)h(data$archecks <- lengtl_de  totaarchetype)
able(data$_counts <- thetype) {
  arcata function(dersity <-annon_div
shShannonsité n de divers - Fonctio-Analysi R-Meta```r
#
ginalCode R Oriex

#### ndty Irsihannon Diveon 1 : Sncti### Fothon

valents Pyt Équictions R ee des Fonse Détailléaly. An 2
