#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  T  e  x  t  C  o  n  t  e  n  t  .  p  y 
#
9
#      Last update: IH240822
#-------------------------------------------------------------------------------

from enum import Enum

class Language(Enum):
        ENGLISH         = 0
        SLOVAK          = 1
        GERMAN          = 2

#IH240812 for debugging only
LoremIpsumHTMLText = """
                        <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. 
                          Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</p>

                        <p>Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, 
                          fringilla vel, aliquet nec, vulputate eget, arcu.</p>

                        <p>In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. 
                          Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. 
                          Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a,</p>
                          <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. 
                          Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
                          Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, 
                          fringilla vel, aliquet nec, vulputate eget, arcu.
                          In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. 
                          Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. 
                          Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a,</p>

                        <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. 
                          Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</p>

                        <p>Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, 
                          fringilla vel, aliquet nec, vulputate eget, arcu.</p>

                        <p>In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. 
                          Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. 
                          Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a,</p>

                        """


MRSM_Texts = [
            {   'enSrcTerm': 'QUIT',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'OPUSTIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'VERLASSEN'},
            ]},
            {   'enSrcTerm': 'STOP',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'ZASTAVIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'STEHENBLEIBEN'},
            ]},
            {   'enSrcTerm': 'FINISH',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'SKONČIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'FERTIGMACHEN'},
            ]},
            {   'enSrcTerm': 'BACK',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'SPÄŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'ZURÜCK'},
            ]},
            {   'enSrcTerm': 'INFO',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'INFO'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'INFO'},
            ]},
            {   'enSrcTerm': '#101',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'App starts in'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'App startet in'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': 'Apka štartuje o'},
            ]},
            {   'enSrcTerm': '#102',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'secs.'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'Sekunden.'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': 'sek.'},
            ]},
             {   'enSrcTerm': '#103',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'Magnetic Resonance Imaging'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'Kernspintomographie'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': 'Magnetická rezonancia'},
            ]},
            {   'enSrcTerm': '#104',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'Institute of Measurement Science, SAS'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'Institut für Messtechnik, SAW'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': 'Ústav merania SAV'},
            ]},
            {   'enSrcTerm': '#105',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'Select organ for imaging...'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'Organ für Untersuchung auswählen...'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': 'Vyber orgán, ktorý chceš vyšetriť...'},
            ]},
            {   'enSrcTerm': '#106',
                'trsl': [{'tgtLng':  Language.ENGLISH, 'tgtTerm': 'This is text1'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'Das ist Text1'},
                         {'tgtLng':  Language.SLOVAK,  'tgtTerm': """                                   
                        <p style="font-size: 40px">
                        <b>O čom to je?</b>
                        </p>
                          
                        <div style="font-size:30px">
                          
                        <p>
                        Toto je model zariadenia, ktoré sa nazýva <b>tomograf na báze magnetickej rezonancie</b> (často sa hovorí <i>MR tomograf</i>).
                        Je to zariadenie, ktoré slúži lekárom na zobrazovanie orgánov vo vnútri ľudského tela. Orgány vidíme tak, 
                        ako keby sme telo rozrezali, buď pozdĺžne od hlavy k nohám, alebo priečne.                        
                        </p>
                          
                        <div style="margin-top:100px; margin-bottom:100px;">
                        <table>  
                        <tr>
                            <td><img  src="resources/images/Free-Max/Head/2a_Head_t1_tse_dark-fl_sag_p4_DRB.jpg" height="250"></td>
                            <td style="padding-left:40px">Napríklad na tomto obrázku vidíme, ako vyzerá ľudská hlava, keby sme ju rozrezali na pravú a ľavú polovicu.</td>
                        </tr>
                        </table>
                        </div>
                        
                        <p>
                        Pri vyšetrení je potrebné zasunúť telo pacienta do tunela vo veľkej skrini tvaru bubna. 
                        Vyšetrenie je úplne bezbolestné, ale pacient počas neho počuje rôzne zvuky, 
                        pripomínajúce praskanie alebo trúbenie. 
                        Náš model pracuje rýchlo, ale v skutočnosti trvá celá procedúra asi dvadsať minút.
                        </p>
                          
                        <div style="margin-top:100px; margin-bottom:100px;">
                        <p><b>Ak Vás zaujíma podrobnejšie, ako to celé funguje, čítajte ďalej</b></p>  
                        
                        <p>
                        Magnetická rezonancia (správnejšie <i>nukleárna</i> magnetická rezonancia) je fyzikálny jav. 
                        Prejavuje sa vtedy, keď sa hmota nachádza vo vonkajšom magnetickom poli. Vtedy sa jadrá atómov, 
                        z ktorých je hmota zložená, nastavia do smeru magnetického poľa (podobne ako detské hojdačky v kľude
                        visia kolmo nadol, pretože na ne pôsobí zemská príťažlivosť). Z takéhoto stavu ich možno vychýliť
                        krátkym pôsobením iného magnetického poľa (ako keď do stojacej hojdačky šťuchneme). Jadrá atómov sa
                        začnú pohybovať a snažia sa vrátiť do pôvodného stavu (hojdačka sa rozhojdá a postupne sa vracia do pôvodnej polohy).
                        V akom rytme (<i>frekvencii</i>) sa hojdačka kýve, záleží okrem iného na tom, či na nej sedí veľké alebo malé dieťa. Podobne je to
                        aj u atómov. Keď si budeme všímať hojdanie, môžeme usúdiť, aké je dieťa veľké (správnejšie: <i>ťažké</i>), a to bez toho,
                        aby sme dieťa priamo videli. Ešte lepšie to uvidíme, keď sa rovnako veľké deti na hojdačkách pochytajú za ruky, pretože vtedy
                        sa po chvíli budú všetky hojdať rovnako dopredu-dozadu. A tak isto sa správajú aj atómy: nechytajú sa za ruky, 
                        ale sú vzájomne prepojené, pretože sú blízko seba. A my môžeme usúdiť, aké majú vlastnosti (napríklad či sú to atómy 
                        tvoriace kosti alebo svaly) bez toho, aby sme do tela zasiahli.
                        </p>
                          
                    
                        <div style="margin-top:100px; margin-bottom:100px;">
                        <table>  
                        <tr>                            
                            <td><p><img src="resources/images/diverse/MRSM_fullview_240722.jpg" height="250"></td>  
                            <td style="padding-left:40px">
                            V tomografe vytvárame magnetické polia pomocou veľkých a menších elektromagnetov. Ten najväčší
                            je v tvare veľkého bubna (to je tá veľká bielo-žltá skrinka, v skutočnosti je veľká asi ako auto). 
                            Uprostred má valcový otvor (tunel), do ktorého sa pacient na pohyblivej posteli
                            automaticky zasunie. Potom sa začnú zapínať a vypínať rôzne menšie magnety, a my meriame, ako sa atómy "hojdajú".
                            Z veľkého počtu takýchto meraní potom zostavíme obrázok, v ktorom každý malý bodík (<i>pixel</i>) znamená
                            skupinu "hojdačiek", a lekár vie určiť, či sú tieto hojdačky (<i>tkanivá</i> v ľudskom tele) zdravé, alebo ich trápi nejaká choroba.
                          </td>
                        </tr>
                        </table>
                        </div>

                            
                        <div style="font-size:15px">                        
                        <p style="margin-top:50px; ">
                        Tento model vytvorili pracovníci <b>Ústavu merania Slovenskej akadémie vied v Bratislave</b>, 
                        kde sa zaoberajú výskumom a konštruovaním naozajstných MR tomografov a prispievajú tak 
                        k zlepšovaniu zdravotnej starostlivosti u nás i vo svete.
                        </p> 
                         
                
                        <p>Obrázky pre tento model sme získali z tohto zdroja:</p>
                        <p><i>https://www.magnetomworld.siemens-healthineers.com/clinical-corner/protocols/dicom-images/deep-resolve-phoenix-images</i></p>
                            
                        
                        <p>Zvukové nahrávky pre tento model sme získali z tohto zdroja:</p>
                        <p><i>https://www.youtube.com/watch?v=tHdIv0sUJRI#bottom-sheet</i></p>
                          
                        <p>Všetkým ďakujeme.</p>
                        </div>
                        """
                        
                        #IH240812 for HTML formatting in Qt, see https://doc.qt.io/qt-6/richtext-html-subset.html
                        },
            ]},
        ]
