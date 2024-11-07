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
#      Last update: IH241106
#-------------------------------------------------------------------------------

from enum import Enum

class Language(Enum):
        ENGLISH         = 0
        SLOVAK          = 1
        GERMAN          = 2

class LanguageAbbrev(Enum):
        EN          = Language.ENGLISH
        SK          = Language.SLOVAK
        DE          = Language.GERMAN

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
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'SKONČIŤ'},
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
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'O MR'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'ÜBER MR'},
            ]},
            {   'enSrcTerm': 'WHAT UC',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'ČO VIDÍŠ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'WAS SIEHTS'},
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
                'trsl': [
                        #------------------------------------------------------------------------
                        {'tgtLng':  Language.ENGLISH, 'tgtTerm': """
                        <p style="font-size: 40px">
                        <b>What is this all about?</b>
                        </p>
                          
                        <div style="font-size:30px">
                        
                        <p>
                        This is a model of a device called <b> magnetic resonance scanner</b> (often called <i>MR scanner</i>).
                        It is a device that is used by doctors to visualize  organs inside the human body. We see the organs 
                        as if we had cut the body, either lengthwise from the head to the legs or transversally.
                        </p>
                                                
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <table>
                        <tr>
                        <td><img  src="resources/images/Free-Max/Head/2a_Head_t1_tse_dark-fl_sag_p4_DRB.jpg" height="250"></td>
                        <td style="padding-left:40px">For example, in this image we can see what a human head looks like if we cut it into right and left halves.</td>
                        </tr>
                        </table>
                        </div>
                                                
                        <p>
                        During the examination, it is necessary to push the patient's body into a tunnel in a large drum-shaped enclosure. 
                        The examination is completely painless, but during it the patient is exposed to various sounds, 
                        like crackling or honking. 
                        Our model works quickly, but in reality the whole procedure takes about twenty minutes.
                        </p>
                                                
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <p><b>If you are interested in more detail how it all works, continue reading</b></p>
                                                
                        <p>
                        Magnetic resonance (more precisely <i>nuclear</i> magnetic resonance) is a physical phenomenon. 
                        It manifests itself when matter is exposed to an external magnetic field. At that time, the nuclei of atoms 
                        the matter is composed of, are aligned in the direction of the magnetic field (similar to children swings, which at rest
                        hang vertically because the Earth's gravity). They can be deflected from such a state
                        by a short pulse of another magnetic field (like when we poke a standing swing). The nuclei of atoms
                        begin to move and try to return to their original state (the swing swings and gradually returns to its original position).
                        In which rhythm (<i>frequency</i>) the swing swings depends, among other things, on whether the child is sitting or standing on it. 
                        The atoms behave in a similar way. By observing the swinging, we can tell in which posture the child is, 
                        without seeing the child directly. We will see it even better when children of the same weight on swings hold hands, because then
                        after a while, they will all swing back and forth in the same way. And atoms behave similarly: they don't hold hands, 
                        but they are interconnected because they are close to each other. And we can infer what properties they have (for example, whether they are atoms 
                        forming bones or muscles) without interfering with the body.
                        </p>
                                                
                                            
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <table>
                        <tr>
                        <td><p><img src="resources/images/diverse/MRSM_fullview_240722.jpg" height="250"></td>
                        <td style="padding-left:40px">
                        In a tomograph, we create magnetic fields using large and smaller electromagnets. The largest one
                        is shaped like a big drum (that's the big white and yellow box, in fact it's about the size of a car). 
                        It has a cylindrical hole (tunnel) in the middle, into which the patient on a movable bed
                        is automatically pushed. Then various smaller magnets begin to turn on and off, and we measure how the atoms "swing".
                        From a large number of such measurements, we then compile a picture in which each small dot (<i>pixel</i>) means
                        a group of "swings", and the doctor can determine whether these swings (<i>tissues</i> in the human body) are healthy or suffer from some disease.
                        </td>
                        </tr>
                        </table>
                        </div>

                                                    
                        <div style="font-size:15px">
                        <p style="margin-top:50px; ">
                        This model was created by the scientists of the <b>Institute of Measurement Science of the Slovak Academy of Sciences in Bratislava</b>, 
                        where they are engaged in research and construction of real MR tomographs and thus contribute 
                        to improvement of health care in our country and in the world.
                        </p> 
                                                
                                        
                        <p>We got the images for this model from this source:</p>
                        <p><i>https://www.magnetomworld.siemens-healthineers.com/clinical-corner/protocols/dicom-images/deep-resolve-phoenix-images</i></p>
                                                    
                                                
                        <p>We obtained the audio recordings for this model from this source:</p>
                        <p><i>https://www.youtube.com/watch?v=tHdIv0sUJRI#bottom-sheet</i></p>
                                                
                        <p>Thank you all.</p>
                        </div>
                        """                        
                        },

                        #------------------------------------------------------------------------
                        {'tgtLng':  Language.GERMAN,  'tgtTerm': """
                        <p style="font-size: 40px">
                        <b>Worum geht es hier?</b>
                        </p>
                                                
                        <div style="font-size:30px">
                                                
                        <p>
                        Hierbei handelt es sich um ein Modell eines Geräts, das als <b>Kernspintomograph</b> bezeichnet wird und auf <b>Kernspinresonanz</b> basiert (oft auch <i>MR-Tomograph genannt</i>).
                        Es ist ein Gerät, das von Ärzten verwendet wird, um Organe im menschlichen Körper abzubilden. Wir sehen die Organe so,
                        als hätten wir den Körper durchgeschnitten, entweder länglich vom Kopf bis zu den Beinen oder quer.
                        </p>
                                                
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <table>
                        <tr>
                        <td><img  src="resources/images/Free-Max/Head/2a_Head_t1_tse_dark-fl_sag_p4_DRB.jpg" height="250"></td>
                        <td style="padding-left:40px">Zum Beispiel können wir in diesem Bild sehen, wie ein menschlicher Kopf aussehen würde, 
                        wenn wir ihn in rechte und linke Hälften schneiden.</td>
                        </tr>
                        </table>
                        </div>
                                                
                        <p>
                        Während der Untersuchung ist es notwendig, den Körper des Patienten in einen Tunnel in einem großen trommelförmigen Schrank einzuführen. 
                        Die Untersuchung ist völlig schmerzlos, aber der Patient hört während der Untersuchung verschiedene Geräusche, 
                        die an Knistern oder Hupen erinnern. 
                        Unser Modell funktioniert schnell, aber in Wirklichkeit dauert der ganze Vorgang etwa zwanzig Minuten.
                        </p>
                                                
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <p><b>Wenn Sie mehr darüber erfahren möchten, wie das alles funktioniert, lesen Sie weiter</b></p>
                                                
                        <p>
                        Die Kernspintresonanz ist ein physikalisches Phänomen. 
                        Sie manifestiert sich, wenn sich Materie in einem externen Magnetfeld befindet. Zu dieser Zeit werden die Atomkerne, 
                        aus denen sich die Masse zusammensetzt, werden in Richtung des Magnetfeldes eingestellt (ähnlich wie bei Kinderschaukeln im Ruhezustand
                        senkrecht nach unten hängen, weil die Schwerkraft der Erde auf sie einwirkt). Sie können aus einem solchen Zustand abgelenkt werden
                        durch eine kurze Wirkung eines anderen Magnetfeldes (wie wenn wir eine stehende Schaukel anstoßen). Die Kerne der Atome
                        Sie beginnen sich zu bewegen und versuchen, in ihren ursprünglichen Zustand zurückzukehren (die Schaukel schwingt und kehrt allmählich in ihre ursprüngliche Position zurück).
                        In welchem Rhythmus (<i>Frequenz</i>) die Schaukel schwingt, hängt unter anderem davon ab, ob das Kind darauf sitzt or steht. Ähnlich
                        sogar in Atomen. Durch das Bemerken des Schaukelns können wir beurteilen, in welcher Position das Kind ist, ohne
                        damit wir das Kind direkt sehen können. Wir werden es noch besser sehen, wenn Kinder gleicher Größe auf Schaukeln Händchen halten, denn dann
                        Nach einer Weile schwingen sie alle auf die gleiche Weise hin und her. Und Atome verhalten sich auf die gleiche Weise: Sie halten sich nicht an den Händen, 
                        Aber sie sind miteinander verbunden, weil sie nahe beieinander liegen. Und wir können daraus ableiten, welche Eigenschaften sie haben (z.B. ob sie Atome sind 
                        B. Knochen oder Muskeln bilden), ohne in den Körper einzugreifen.
                        </p>
                                                
                                            
                        <div style="margin-top:100px; margin-bottom:100px;" >
                        <table>
                        <tr>
                        <td><p><img src="resources/images/diverse/MRSM_fullview_240722.jpg" height="250"></td>
                        <td style="padding-left:40px">
                        In einem Tomographen werden Magnetfelder mit großen und kleineren Elektromagneten hergestellt. Der größte Magnet
                         hat die Form einer großen Trommel (das ist die große weiß-gelbe Schachtel, tatsächlich ist sie etwa so groß wie ein Auto). 
                        Es hat in der Mitte ein zylindrisches Loch (Tunnel), in das der Patient auf einem beweglichen Bett
                        automatisch eingeschoben wird. Dann beginnen sich verschiedene kleinere Magnete ein- und auszuschalten, und wir messen, 
                        wie die Atomkerne "schwingen".
                        Aus einer Vielzahl solcher Messungen stellen wir dann ein Bild zusammen, in dem jeder kleine Punkt (<i>Pixel</i>)
                        eine Gruppe von "Schaukeln" darstellt, und der Arzt kann feststellen, 
                         ob diese Schaukeln (<i>Gewebe</I> im menschlichen Körper) gesund sind oder an einer Krankheit leiden.
                        </td>
                        </tr>
                        </table>
                        </div>

                                                    
                        <div style="font-size:15px">
                        <p style="margin-top:50px; ">
                        Dieses Modell wurde von den Mitarbeitern des <b>Instituts für Messtechnik der Slowakischen Akademie der Wissenschaften in Bratislava</b>
                        hergestellt , 
                        In diesem Institut beschäftigen sie sich mit der Forschung und der Konstruktion von echten MR-Tomographen und damit zur 
                        tragen sie zu Verbesserung der Gesundheitsversorgung in unserem Land und in der ganzen Welt.
                        </p> 
                                                
                                        
                        <p>Die Bilder für dieses Modell haben wir aus dieser Quelle:</p>
                        <p><i>https://www.magnetomworld.siemens-healthineers.com/clinical-corner/protocols/dicom-images/deep-resolve-phoenix-images</i></p>
                                                    
                                                
                        <p>Die Audioaufnahmen für dieses Modell haben wir aus dieser Quelle:</p>
                        <p><i>https://www.youtube.com/watch?v=tHdIv0sUJRI#bottom-sheet</i></p>
                                                
                        <p>Vielen Dank an alle.</p>
                        </div>                        
                        """
                        },
                        
                        #------------------------------------------------------------------------
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
                        #------------------------------------------------------------------------                                                
                        },
                        #IH240812 for HTML formatting in Qt, see https://doc.qt.io/qt-6/richtext-html-subset.html
            ]},
        ]
