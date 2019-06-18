<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs marc" version="2.0">
    <!--  this stylesheet will take OAI marc records from the Columbia University Libraries ArchivesSpace instance and clean them up for Voyager import.  -->
    
 <xsl:output indent="yes"/>
 
    <!--  The initial match kicks of a loop that ignores the OAI XML apparatus -->
    
    <xsl:template match="/">
        <collection>
            <xsl:for-each select="repository/record">
                <xsl:apply-templates select="."/>
            </xsl:for-each>
        </collection>
    </xsl:template>
    
    <!--  Only records that have /resources/ in identifier are passed to template (to exclude archival_objects, etc.) -->
    <xsl:template match="record">
        <xsl:if test="contains(header/identifier, '/resources/')">
            <xsl:apply-templates select="metadata/marc:collection/marc:record"/>
        </xsl:if>
    </xsl:template>
    
    <!--    three templates copy everything sans namespace -->
    <xsl:template match="*">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:element>
    </xsl:template>

    <!-- template to copy attributes -->
    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <!-- template to copy the rest of the nodes -->
    <xsl:template match="comment() | text() | processing-instruction()">
        <xsl:copy/>
    </xsl:template>
    <!--    end three templates     -->


    <!--  remove elements without content (extra 035 and 040s etc being exported by AS for some reason) -->
    <xsl:template match="marc:datafield[not(marc:subfield)]">
        <!--        do nothing  -->
    </xsl:template>
    
    <!--   remove "empty" subfields having no text content --> 
    <xsl:template match="marc:subfield[not(normalize-space(text()))]">
        <!--        do nothing  -->
    </xsl:template>

    <!--    reformat 035 CULASPC to local practice, add NNC 035 field -->
    <!--    commented out second test, no longer applicable for dupe NNC 035s: added test for adjacent silbing with 035 containing NNC; if exists, do nothing. If not, create.    -->
    <!--  see below, added a control field 003 to allow for proper 035 building upon ingest into voyager  -->
    <xsl:template match="marc:datafield[@tag = '035'][marc:subfield[contains(., 'CULASPC')]]">
        <datafield ind1=" " ind2=" " tag="035">
            <subfield code="a">
                <xsl:text>(NNC)CULASPC:voyager:</xsl:text>
                <xsl:value-of select="normalize-space(substring-after(., '-'))"/>
            </subfield>
        </datafield>
        <!-- <xsl:if test="not(../marc:datafield[@tag='035'][marc:subfield[contains(., 'NNC')]])">
            <datafield ind1=" " ind2=" " tag="035">
                <subfield code="a">
                    <xsl:text>(NNC)</xsl:text>
                    <xsl:value-of select="normalize-space(substring-after(., '-'))"/>
                </subfield>
            </datafield>    
        </xsl:if>-->
    </xsl:template>


    <!--  add repo to 040 field; test for UA in 852$j  -->
    <xsl:template match="marc:datafield[@tag = '040'][marc:subfield]">

    <!-- check if is UA -->
    <xsl:variable name="isUA">
        <xsl:if test="../marc:datafield[@tag = '852']/marc:subfield[@code = 'j'][contains(., 'UA')]">Y</xsl:if>
    </xsl:variable>
        <!-- check if is OH -->
    <xsl:variable name="isOH">
            <xsl:if test="../marc:datafield[@tag = '852']/marc:subfield[@code = 'j'][contains(., 'OHAC')]">Y</xsl:if>
    </xsl:variable>
        

        <datafield ind1=" " ind2=" " tag="040">
            <subfield code="a">
                <xsl:choose>
                    <xsl:when test="$isUA='Y'">
<xsl:text>NNC-UA</xsl:text>      
                    </xsl:when>
                    <xsl:when test="$isOH='Y'">
                        <xsl:text>NNC-OH</xsl:text>      
                    </xsl:when>
                    <xsl:otherwise> 
                        <xsl:value-of select="marc:subfield[@code='a']"/>
                    </xsl:otherwise>
                </xsl:choose>
            </subfield>
            <subfield code="b">
                <!-- <xsl:value-of select="marc:subfield[@code = 'b']"/> -->
                <xsl:text>eng</xsl:text>
                <!-- NOTE: this is a workaround for a bug that populates 040$b with the wrong data; see https://archivesspace.atlassian.net/browse/ANW-827 -->
            </subfield>
            <subfield code="c">
                <xsl:choose>
                    <xsl:when test="$isUA='Y'">
                        <xsl:text>NNC-UA</xsl:text>                                            
                    </xsl:when>
                    <xsl:when test="$isOH='Y'">
                        <xsl:text>NNC-OH</xsl:text>                                            
                    </xsl:when>
                    <xsl:otherwise> 
                        <xsl:value-of select="marc:subfield[@code='c']"/>
                    </xsl:otherwise>
                </xsl:choose>
            </subfield>
            <subfield code="e">
                <xsl:value-of select="marc:subfield[@code = 'e']"/>
            </subfield>
        </datafield>
        
     </xsl:template>

    <!--    If there are 041 with empty subfields AND there are no 546 languages to parse, delete -->
    <xsl:template
        match="marc:datafield[@tag = '041'][marc:subfield[not(normalize-space(text()))]][../not(marc:datafield[@tag = '546'])]">
            <!-- Do nothing -->
    </xsl:template>

    <!--    if a 041 and 546 exists, copy 546 and then generate 041s from the language strings by refering to the iso 639-2b code list below -->
    <xsl:template
        match="marc:datafield[@tag = '041'][marc:subfield][../marc:datafield[@tag = '546']]">
        <!-- tokenize, remove punctuation, and take distinctive values for 546 language field -->
        <datafield ind1=" " ind2=" " tag="041">
            <xsl:for-each
                select="distinct-values(tokenize(translate(../marc:datafield[@tag = '546'][1]/marc:subfield[@code = 'a']/text(), '.;:,', ''), ' '))">
                <xsl:choose>
                    <!-- the test to compare the token to the lang list; if matches, populate with the code -->
                    <xsl:when test=". = $langCodes/lang/b">
                        <xsl:variable name="selectedLang">
                            <xsl:value-of select="."/>
                        </xsl:variable>
                        <subfield code="a">
                            <xsl:value-of
                                select="$langCodes/lang/a[following-sibling::b[1] = $selectedLang]"
                            />
                        </subfield>
                    </xsl:when>
                    <xsl:otherwise>
                        <!--                    do nothing if the token doesn't match the code list-->
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </datafield>
    </xsl:template>

    <!--  add "bulk" in front of 245 $g field  -->
    <xsl:template match="marc:datafield[@tag = '245']/marc:subfield[@code = 'g']">
        <subfield code="g">
            <xsl:text>bulk </xsl:text>
            <xsl:value-of select="."/>
        </subfield>
    </xsl:template>
    
    <!--  add 1st indicator 1 to 544 related materials  -->
    <xsl:template match="marc:datafield[@tag = '544']">
        <datafield ind1="1" ind2=" " tag="544">
        <subfield code="d">
            <xsl:value-of select="marc:subfield[@code='d']"/>
        </subfield>
        </datafield>
    </xsl:template>
    
    <!--  remove subfield e from 1XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '1')]]/marc:subfield[@code = 'e']">
        <!--     do nothing   -->
    </xsl:template>

    <!--  remove subfield e from 6XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '6')]]/marc:subfield[@code = 'e']">
        <!--     do nothing   -->
    </xsl:template>

    <!--  remove subfield e from 7XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '7')]]/marc:subfield[@code = 'e']">
        <!--     do nothing   -->
    </xsl:template>


    <!--  remove subfield 0 from 6XX when there are subject subdivisions ($v, $x, $y, $z)  -->
    
    <xsl:template match="marc:datafield[@tag[starts-with(., '6')]]/marc:subfield[@code = '0'][../marc:subfield/@code[contains('vxyz',.)]]">
             <!--     do nothing   -->
    </xsl:template>
    

<!--  add $3 "Finding aid" to 856 fields -->
    <xsl:template match="marc:datafield[@tag = '856']">
        <datafield ind1="4" ind2="2" tag="856">
            <subfield code="u">
                <xsl:value-of select="marc:subfield[@code='u']"/>    
            </subfield>
            <!--<subfield code="z">
                <xsl:value-of select="marc:subfield[@code='z']"/>
            </subfield>-->
            <subfield code="3">
                <xsl:text>Finding aid</xsl:text>
            </subfield>
        </datafield>
    </xsl:template>

    <!-- For corporate names (110 and 610), remove trailing comma if no subordinate name available. -->
    <xsl:template match="marc:datafield[@tag = '110' or @tag = '610']/marc:subfield[@code='a']">
        <subfield code="a">
            <xsl:choose>
                <xsl:when test="../marc:subfield[@code='b']">
                    <!--  there is a $b following, keep punctuation   -->
                    <xsl:value-of select="."/>  
                </xsl:when>
                <xsl:otherwise>
                    <!--  there is no $b following, strip punctuation   -->
                    <xsl:call-template name="stripComma"/>
                </xsl:otherwise>
            </xsl:choose>
        </subfield>
    </xsl:template>
      

    <!-- For 110$b and 610$b, remove trailing comma. -->
    <xsl:template match="marc:datafield[@tag = '110' or @tag = '610']/marc:subfield[@code='b']">
        <subfield code="b">
                    <xsl:call-template name="stripComma"/>
        </subfield>
    </xsl:template>
    
    

    <!-- Strip trailing punctuation from specified text nodes  -->
    <xsl:template name="stripComma">
        <xsl:analyze-string select="normalize-space(.)" regex="^(.*)(,)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select='.'/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>
    
    

    <!--    reorder elements -->
    <!-- Grab the record, copy the leader and sort the control and data fields. -->
    <xsl:template match="marc:record">        
        <record>
            <xsl:element name="leader">
                <xsl:value-of select="marc:leader"/>
            </xsl:element>
            <!--           for prod, move 099 to 001 -->
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">001</xsl:attribute>
                <xsl:value-of select="marc:datafield[@tag = '099']/marc:subfield[@code = 'a']"/>
            </xsl:element>
            <!--         added 003 to allow for creation of 035 upon import   -->
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">003</xsl:attribute>
                <xsl:text>NNC</xsl:text>
            </xsl:element>
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">008</xsl:attribute>
                <xsl:value-of select="marc:controlfield"/>
            </xsl:element>
            <xsl:for-each select="marc:datafield">
                <xsl:sort select="@tag"/>
                <xsl:apply-templates select="."/>
            </xsl:for-each>
        </record>
            
    </xsl:template>

    <!--    remove colons from beginning of fields -->
    <xsl:template match="marc:subfield[starts-with(., ':')]">
        <xsl:element name="subfield">
            <xsl:attribute name="code">
                <xsl:value-of select="@code"/>
            </xsl:attribute>
            <xsl:copy-of select="normalize-space(translate(., ':', ''))"/>
        </xsl:element>
    </xsl:template>

    <!--    remove commas from end of sub field d -->
    <xsl:template match="marc:subfield[@code = 'd']">
        <subfield code="d">
            <xsl:call-template name="stripComma"/>
        </subfield>
    </xsl:template>
    
    <xsl:variable name="langCodes">
        <lang>
            <a>aar</a>
            <b>Afar</b>
            <a>abk</a>
            <b>Abkhazian</b>
            <a>ace</a>
            <b>Achinese</b>
            <a>ach</a>
            <b>Acoli</b>
            <a>ada</a>
            <b>Adangme</b>
            <a>ady</a>
            <b>Adyghe Adygei</b>
            <a>afa</a>
            <b>Afro-Asiatic</b>
            <a>afh</a>
            <b>Afrihili</b>
            <a>afr</a>
            <b>Afrikaans</b>
            <a>ain</a>
            <b>Ainu</b>
            <a>aka</a>
            <b>Akan</b>
            <a>akk</a>
            <b>Akkadian</b>
            <a>alb</a>
            <b>Albanian</b>
            <a>ale</a>
            <b>Aleut</b>
            <a>alg</a>
            <b>Algonquian</b>
            <a>alt</a>
            <b>Southern Altai</b>
            <a>amh</a>
            <b>Amharic</b>
            <a>anp</a>
            <b>Angika</b>
            <a>apa</a>
            <b>Apache</b>
            <a>ara</a>
            <b>Arabic</b>
            <a>arc</a>
            <b>Aramaic </b>
            <a>arg</a>
            <b>Aragonese</b>
            <a>arm</a>
            <b>Armenian</b>
            <a>arn</a>
            <b>Mapudungun Mapuche</b>
            <a>arp</a>
            <b>Arapaho</b>
            <a>art</a>
            <b>Artificial</b>
            <a>arw</a>
            <b>Arawak</b>
            <a>asm</a>
            <b>Assamese</b>
            <a>ast</a>
            <b>Asturian Bable Leonese Asturleonese</b>
            <a>ath</a>
            <b>Athapascan</b>
            <a>aus</a>
            <b>Australian</b>
            <a>ava</a>
            <b>Avaric</b>
            <a>ave</a>
            <b>Avestan</b>
            <a>awa</a>
            <b>Awadhi</b>
            <a>aym</a>
            <b>Aymara</b>
            <a>aze</a>
            <b>Azerbaijani</b>
            <a>bad</a>
            <b>Banda</b>
            <a>bai</a>
            <b>Bamileke</b>
            <a>bak</a>
            <b>Bashkir</b>
            <a>bal</a>
            <b>Baluchi</b>
            <a>bam</a>
            <b>Bambara</b>
            <a>ban</a>
            <b>Balinese</b>
            <a>baq</a>
            <b>Basque</b>
            <a>bas</a>
            <b>Basa</b>
            <a>bat</a>
            <b>Baltic</b>
            <a>bej</a>
            <b>Beja Bedawiyet</b>
            <a>bel</a>
            <b>Belarusian</b>
            <a>bem</a>
            <b>Bemba</b>
            <a>ben</a>
            <b>Bengali</b>
            <a>ber</a>
            <b>Berber</b>
            <a>bho</a>
            <b>Bhojpuri</b>
            <a>bih</a>
            <b>Bihari</b>
            <a>bik</a>
            <b>Bikol</b>
            <a>bin</a>
            <b>Bini Edo</b>
            <a>bis</a>
            <b>Bislama</b>
            <a>bla</a>
            <b>Siksika</b>
            <a>bnt</a>
            <b>Bantu</b>
            <a>tib</a>
            <b>Tibetan</b>
            <a>bos</a>
            <b>Bosnian</b>
            <a>bra</a>
            <b>Braj</b>
            <a>bre</a>
            <b>Breton</b>
            <a>btk</a>
            <b>Batak</b>
            <a>bua</a>
            <b>Buriat</b>
            <a>bug</a>
            <b>Buginese</b>
            <a>bul</a>
            <b>Bulgarian</b>
            <a>bur</a>
            <b>Burmese</b>
            <a>byn</a>
            <b>Blin Bilin</b>
            <a>cad</a>
            <b>Caddo</b>
            <a>cai</a>
            <b>Central American Indian</b>
            <a>car</a>
            <b>Galibi Carib</b>
            <a>cat</a>
            <b>Catalan Valencian</b>
            <a>cau</a>
            <b>Caucasian</b>
            <a>ceb</a>
            <b>Cebuano</b>
            <a>cel</a>
            <b>Celtic</b>
            <a>cze</a>
            <b>Czech</b>
            <a>cha</a>
            <b>Chamorro</b>
            <a>chb</a>
            <b>Chibcha</b>
            <a>che</a>
            <b>Chechen</b>
            <a>chg</a>
            <b>Chagatai</b>
            <a>chi</a>
            <b>Chinese</b>
            <a>chk</a>
            <b>Chuukese</b>
            <a>chm</a>
            <b>Mari</b>
            <a>chn</a>
            <b>Chinook jargon</b>
            <a>cho</a>
            <b>Choctaw</b>
            <a>chp</a>
            <b>Chipewyan Dene Suline</b>
            <a>chr</a>
            <b>Cherokee</b>
            <a>chu</a>
            <b>Slavonic</b>
            <a>chv</a>
            <b>Chuvash</b>
            <a>chy</a>
            <b>Cheyenne</b>
            <a>cmc</a>
            <b>Chamic</b>
            <a>cnr</a>
            <b>Montenegrin</b>
            <a>cop</a>
            <b>Coptic</b>
            <a>cor</a>
            <b>Cornish</b>
            <a>cos</a>
            <b>Corsican</b>
            <a>cre</a>
            <b>Cree</b>
            <a>crh</a>
            <b>Crimean</b>
            <a>crp</a>
            <b>Creoles and pidgins</b>
            <a>csb</a>
            <b>Kashubian</b>
            <a>cus</a>
            <b>Cushitic</b>
            <a>wel</a>
            <b>Welsh</b>
            <a>cze</a>
            <b>Czech</b>
            <a>dak</a>
            <b>Dakota</b>
            <a>dan</a>
            <b>Danish</b>
            <a>dar</a>
            <b>Dargwa</b>
            <a>day</a>
            <b>Land Dayak</b>
            <a>del</a>
            <b>Delaware</b>
            <a>den</a>
            <b>Slave (Athapascan)</b>
            <a>dgr</a>
            <b>Dogrib</b>
            <a>din</a>
            <b>Dinka</b>
            <a>div</a>
            <b>Divehi Dhivehi Maldivian</b>
            <a>doi</a>
            <b>Dogri</b>
            <a>dra</a>
            <b>Dravidian</b>
            <a>dsb</a>
            <b>Lower Sorbian</b>
            <a>dua</a>
            <b>Duala</b>
            <a>dut</a>
            <b>Dutch</b>
            <a>dyu</a>
            <b>Dyula</b>
            <a>dzo</a>
            <b>Dzongkha</b>
            <a>efi</a>
            <b>Efik</b>
            <a>egy</a>
            <b>Egyptian</b>
            <a>eka</a>
            <b>Ekajuk</b>
            <a>gre</a>
            <b>Greek</b>
            <a>elx</a>
            <b>Elamite</b>
            <a>eng</a>
            <b>English</b>
            <a>epo</a>
            <b>Esperanto</b>
            <a>est</a>
            <b>Estonian</b>
            <a>baq</a>
            <b>Basque</b>
            <a>ewe</a>
            <b>Ewe</b>
            <a>ewo</a>
            <b>Ewondo</b>
            <a>fan</a>
            <b>Fang</b>
            <a>fao</a>
            <b>Faroese</b>
            <a>fat</a>
            <b>Fanti</b>
            <a>fij</a>
            <b>Fijian</b>
            <a>fil</a>
            <b>Filipino</b>
            <a>fin</a>
            <b>Finnish</b>
            <a>fiu</a>
            <b>Finno-Ugrian</b>
            <a>fon</a>
            <b>Fon</b>
            <a>fre</a>
            <b>French</b>
            <a>ful</a>
            <b>Fulah</b>
            <a>fur</a>
            <b>Friulian</b>
            <a>gaa</a>
            <b>Ga</b>
            <a>gay</a>
            <b>Gayo</b>
            <a>gba</a>
            <b>Gbaya</b>
            <a>gem</a>
            <b>Germanic</b>
            <a>geo</a>
            <b>Georgian</b>
            <a>ger</a>
            <b>German</b>
            <a>gez</a>
            <b>Geez</b>
            <a>gil</a>
            <b>Gilbertese</b>
            <a>gla</a>
            <b>Scottish</b>
            <a>gle</a>
            <b>Irish</b>
            <a>glg</a>
            <b>Galician</b>
            <a>glv</a>
            <b>Manx</b>
            <a>gon</a>
            <b>Gondi</b>
            <a>gor</a>
            <b>Gorontalo</b>
            <a>got</a>
            <b>Gothic</b>
            <a>grb</a>
            <b>Grebo</b>
            <a>grn</a>
            <b>Guarani</b>
            <a>gsw</a>
            <b>Swiss</b>
            <a>guj</a>
            <b>Gujarati</b>
            <a>gwi</a>
            <b>Gwich'in</b>
            <a>hai</a>
            <b>Haida</b>
            <a>hat</a>
            <b>Haitian</b>
            <a>hau</a>
            <b>Hausa</b>
            <a>haw</a>
            <b>Hawaiian</b>
            <a>heb</a>
            <b>Hebrew</b>
            <a>her</a>
            <b>Herero</b>
            <a>hil</a>
            <b>Hiligaynon</b>
            <a>him</a>
            <b>Himachali Western Pahari</b>
            <a>hin</a>
            <b>Hindi</b>
            <a>hit</a>
            <b>Hittite</b>
            <a>hmn</a>
            <b>Hmong Mong</b>
            <a>hmo</a>
            <b>Hiri Motu</b>
            <a>hrv</a>
            <b>Croatian</b>
            <a>hsb</a>
            <b>Upper Sorbian</b>
            <a>hun</a>
            <b>Hungarian</b>
            <a>hup</a>
            <b>Hupa</b>
            <a>iba</a>
            <b>Iban</b>
            <a>ibo</a>
            <b>Igbo</b>
            <a>ice</a>
            <b>Icelandic</b>
            <a>ido</a>
            <b>Ido</b>
            <a>iii</a>
            <b>Sichuan Yi Nuosu</b>
            <a>ijo</a>
            <b>Ijo</b>
            <a>iku</a>
            <b>Inuktitut</b>
            <a>ile</a>
            <b>Interlingue Occidental</b>
            <a>ilo</a>
            <b>Iloko</b>
            <a>ina</a>
            <b>Interlingua (International Auxiliary Language Association)</b>
            <a>inc</a>
            <b>Indic</b>
            <a>ind</a>
            <b>Indonesian</b>
            <a>ine</a>
            <b>Indo-European</b>
            <a>inh</a>
            <b>Ingush</b>
            <a>ipk</a>
            <b>Inupiaq</b>
            <a>ira</a>
            <b>Iranian</b>
            <a>iro</a>
            <b>Iroquoian</b>
            <a>ice</a>
            <b>Icelandic</b>
            <a>ita</a>
            <b>Italian</b>
            <a>jav</a>
            <b>Javanese</b>
            <a>jbo</a>
            <b>Lojban</b>
            <a>jpn</a>
            <b>Japanese</b>
            <a>jpr</a>
            <b>Judeo-Persian</b>
            <a>jrb</a>
            <b>Judeo-Arabic</b>
            <a>kaa</a>
            <b>Kara-Kalpak</b>
            <a>kab</a>
            <b>Kabyle</b>
            <a>kac</a>
            <b>Kachin Jingpho</b>
            <a>kal</a>
            <b>Kalaallisut</b>
            <a>kam</a>
            <b>Kamba</b>
            <a>kan</a>
            <b>Kannada</b>
            <a>kar</a>
            <b>Karen</b>
            <a>kas</a>
            <b>Kashmiri</b>
            <a>geo</a>
            <b>Georgian</b>
            <a>kau</a>
            <b>Kanuri</b>
            <a>kaw</a>
            <b>Kawi</b>
            <a>kaz</a>
            <b>Kazakh</b>
            <a>kbd</a>
            <b>Kabardian</b>
            <a>kha</a>
            <b>Khasi</b>
            <a>khi</a>
            <b>Khoisan</b>
            <a>khm</a>
            <b>Central Khmer</b>
            <a>kho</a>
            <b>Khotanese Sakan</b>
            <a>kik</a>
            <b>Kikuyu Gikuyu</b>
            <a>kin</a>
            <b>Kinyarwanda</b>
            <a>kir</a>
            <b>Kirghiz Kyrgyz</b>
            <a>kmb</a>
            <b>Kimbundu</b>
            <a>kok</a>
            <b>Konkani</b>
            <a>kom</a>
            <b>Komi</b>
            <a>kon</a>
            <b>Kongo</b>
            <a>kor</a>
            <b>Korean</b>
            <a>kos</a>
            <b>Kosraean</b>
            <a>kpe</a>
            <b>Kpelle</b>
            <a>krc</a>
            <b>Karachay-Balkar</b>
            <a>krl</a>
            <b>Karelian</b>
            <a>kro</a>
            <b>Kru</b>
            <a>kru</a>
            <b>Kurukh</b>
            <a>kua</a>
            <b>Kuanyama Kwanyama</b>
            <a>kum</a>
            <b>Kumyk</b>
            <a>kur</a>
            <b>Kurdish</b>
            <a>kut</a>
            <b>Kutenai</b>
            <a>lad</a>
            <b>Ladino</b>
            <a>lah</a>
            <b>Lahnda</b>
            <a>lam</a>
            <b>Lamba</b>
            <a>lao</a>
            <b>Lao</b>
            <a>lat</a>
            <b>Latin</b>
            <a>lav</a>
            <b>Latvian</b>
            <a>lez</a>
            <b>Lezghian</b>
            <a>lim</a>
            <b>Limburgan Limburger Limburgish</b>
            <a>lin</a>
            <b>Lingala</b>
            <a>lit</a>
            <b>Lithuanian</b>
            <a>lol</a>
            <b>Mongo</b>
            <a>loz</a>
            <b>Lozi</b>
            <a>ltz</a>
            <b>Luxembourgish</b>
            <a>lua</a>
            <b>Luba-Lulua</b>
            <a>lub</a>
            <b>Luba-Katanga</b>
            <a>lug</a>
            <b>Ganda</b>
            <a>lui</a>
            <b>Luiseno</b>
            <a>lun</a>
            <b>Lunda</b>
            <a>luo</a>
            <b>Luo (Kenya and Tanzania)</b>
            <a>lus</a>
            <b>Lushai</b>
            <a>mac</a>
            <b>Macedonian</b>
            <a>mad</a>
            <b>Madurese</b>
            <a>mag</a>
            <b>Magahi</b>
            <a>mah</a>
            <b>Marshallese</b>
            <a>mai</a>
            <b>Maithili</b>
            <a>mak</a>
            <b>Makasar</b>
            <a>mal</a>
            <b>Malayalam</b>
            <a>man</a>
            <b>Mandingo</b>
            <a>mao</a>
            <b>Maori</b>
            <a>map</a>
            <b>Austronesian</b>
            <a>mar</a>
            <b>Marathi</b>
            <a>mas</a>
            <b>Masai</b>
            <a>may</a>
            <b>Malay</b>
            <a>mdf</a>
            <b>Moksha</b>
            <a>mdr</a>
            <b>Mandar</b>
            <a>men</a>
            <b>Mende</b>
            <a>mga</a>
            <b>Irish, Middle (900-1200)</b>
            <a>mic</a>
            <b>Mi'kmaq Micmac</b>
            <a>min</a>
            <b>Minangkabau</b>
            <a>mis</a>
            <b>Uncoded</b>
            <a>mac</a>
            <b>Macedonian</b>
            <a>mkh</a>
            <b>Mon-Khmer</b>
            <a>mlg</a>
            <b>Malagasy</b>
            <a>mlt</a>
            <b>Maltese</b>
            <a>mnc</a>
            <b>Manchu</b>
            <a>mni</a>
            <b>Manipuri</b>
            <a>mno</a>
            <b>Manobo</b>
            <a>moh</a>
            <b>Mohawk</b>
            <a>mon</a>
            <b>Mongolian</b>
            <a>mos</a>
            <b>Mossi</b>
            <a>mao</a>
            <b>Maori</b>
            <a>may</a>
            <b>Malay</b>
            <a>mul</a>
            <b>Multiple</b>
            <a>mun</a>
            <b>Munda</b>
            <a>mus</a>
            <b>Creek</b>
            <a>mwl</a>
            <b>Mirandese</b>
            <a>mwr</a>
            <b>Marwari</b>
            <a>bur</a>
            <b>Burmese</b>
            <a>myn</a>
            <b>Mayan</b>
            <a>myv</a>
            <b>Erzya</b>
            <a>nah</a>
            <b>Nahuatl</b>
            <a>nai</a>
            <b>North American Indian</b>
            <a>nap</a>
            <b>Neapolitan</b>
            <a>nau</a>
            <b>Nauru</b>
            <a>nav</a>
            <b>Navajo Navaho</b>
            <a>nbl</a>
            <b>Ndebele, South South Ndebele</b>
            <a>nde</a>
            <b>Ndebele, North North Ndebele</b>
            <a>ndo</a>
            <b>Ndonga</b>
            <a>nds</a>
            <b>Low German Low Saxon German, Low Saxon, Low</b>
            <a>nep</a>
            <b>Nepali</b>
            <a>new</a>
            <b>Nepal Bhasa Newari</b>
            <a>nia</a>
            <b>Nias</b>
            <a>nic</a>
            <b>Niger-Kordofanian</b>
            <a>niu</a>
            <b>Niuean</b>
            <a>dut</a>
            <b>Dutch</b>
            <a>dut</a>
            <b>Flemish</b>   
            <a>nno</a>
            <b>Norwegian</b>
            <a>nob</a>
            <b>Bokmål</b>
            <a>nog</a>
            <b>Nogai</b>
            <a>non</a>
            <b>Norse, Old</b>
            <a>nor</a>
            <b>Norwegian</b>
            <a>nqo</a>
            <b>N'Ko</b>
            <a>nso</a>
            <b>Pedi</b>
            <a>nub</a>
            <b>Nubian</b>
            <a>nwc</a>
            <b>Classical Newari Old Newari Classical Nepal Bhasa</b>
            <a>nya</a>
            <b>Chichewa Chewa Nyanja</b>
            <a>nym</a>
            <b>Nyamwezi</b>
            <a>nyn</a>
            <b>Nyankole</b>
            <a>nyo</a>
            <b>Nyoro</b>
            <a>nzi</a>
            <b>Nzima</b>
            <a>oci</a>
            <b>Occitan (post 1500)</b>
            <a>oji</a>
            <b>Ojibwa</b>
            <a>ori</a>
            <b>Oriya</b>
            <a>orm</a>
            <b>Oromo</b>
            <a>osa</a>
            <b>Osage</b>
            <a>oss</a>
            <b>Ossetian Ossetic</b>
            <a>ota</a>
            <b>Turkish, Ottoman (1500-1928)</b>
            <a>oto</a>
            <b>Otomian</b>
            <a>paa</a>
            <b>Papuan</b>
            <a>pag</a>
            <b>Pangasinan</b>
            <a>pal</a>
            <b>Pahlavi</b>
            <a>pam</a>
            <b>Pampanga Kapampangan</b>
            <a>pan</a>
            <b>Panjabi Punjabi</b>
            <a>pap</a>
            <b>Papiamento</b>
            <a>pau</a>
            <b>Palauan</b>
            <a>peo</a>
            <b>Persian, Old (ca.600-400 B.C.)</b>
            <a>per</a>
            <b>Persian</b>
            <a>phi</a>
            <b>Philippine</b>
            <a>phn</a>
            <b>Phoenician</b>
            <a>pli</a>
            <b>Pali</b>
            <a>pol</a>
            <b>Polish</b>
            <a>pon</a>
            <b>Pohnpeian</b>
            <a>por</a>
            <b>Portuguese</b>
            <a>pra</a>
            <b>Prakrit</b>
            <a>pro</a>
            <b>Provençal, Old (to 1500)Occitan, Old (to 1500)</b>
            <a>pus</a>
            <b>Pushto Pashto</b>
            <a>que</a>
            <b>Quechua</b>
            <a>raj</a>
            <b>Rajasthani</b>
            <a>rap</a>
            <b>Rapanui</b>
            <a>rar</a>
            <b>Rarotongan Cook Islands Maori</b>
            <a>roa</a>
            <b>Romance</b>
            <a>roh</a>
            <b>Romansh</b>
            <a>rom</a>
            <b>Romany</b>
            <a>rum</a>
            <b>Romanian Moldavian Moldovan</b>
            <a>run</a>
            <b>Rundi</b>
            <a>rup</a>
            <b>Aromanian Arumanian Macedo-Romanian</b>
            <a>rus</a>
            <b>Russian</b>
            <a>sad</a>
            <b>Sandawe</b>
            <a>sag</a>
            <b>Sango</b>
            <a>sah</a>
            <b>Yakut</b>
            <a>sai</a>
            <b>South American Indian</b>
            <a>sal</a>
            <b>Salishan</b>
            <a>sam</a>
            <b>Samaritan Aramaic</b>
            <a>san</a>
            <b>Sanskrit</b>
            <a>sas</a>
            <b>Sasak</b>
            <a>sat</a>
            <b>Santali</b>
            <a>scn</a>
            <b>Sicilian</b>
            <a>sco</a>
            <b>Scots</b>
            <a>sel</a>
            <b>Selkup</b>
            <a>sem</a>
            <b>Semitic</b>
            <a>sga</a>
            <b>Irish, Old (to 900)</b>
            <a>sgn</a>
            <b>Sign Languages</b>
            <a>shn</a>
            <b>Shan</b>
            <a>sid</a>
            <b>Sidamo</b>
            <a>sin</a>
            <b>Sinhala Sinhalese</b>
            <a>sio</a>
            <b>Siouan</b>
            <a>sit</a>
            <b>Sino-Tibetan</b>
            <a>sla</a>
            <b>Slavic</b>
            <a>slo</a>
            <b>Slovak</b>
            <a>slv</a>
            <b>Slovenian</b>
            <a>sma</a>
            <b>Southern Sami</b>
            <a>sme</a>
            <b>Northern Sami</b>
            <a>smi</a>
            <b>Sami</b>
            <a>smj</a>
            <b>Lule Sami</b>
            <a>smn</a>
            <b>Inari Sami</b>
            <a>smo</a>
            <b>Samoan</b>
            <a>sms</a>
            <b>Skolt Sami</b>
            <a>sna</a>
            <b>Shona</b>
            <a>snd</a>
            <b>Sindhi</b>
            <a>snk</a>
            <b>Soninke</b>
            <a>sog</a>
            <b>Sogdian</b>
            <a>som</a>
            <b>Somali</b>
            <a>son</a>
            <b>Songhai</b>
            <a>sot</a>
            <b>Sotho, Southern</b>
            <a>spa</a>
            <b>Spanish</b>
            <a>alb</a>
            <b>Albanian</b>
            <a>srd</a>
            <b>Sardinian</b>
            <a>srn</a>
            <b>Sranan Tongo</b>
            <a>srp</a>
            <b>Serbian</b>
            <a>srr</a>
            <b>Serer</b>
            <a>ssa</a>
            <b>Nilo-Saharan</b>
            <a>ssw</a>
            <b>Swati</b>
            <a>suk</a>
            <b>Sukuma</b>
            <a>sun</a>
            <b>Sundanese</b>
            <a>sus</a>
            <b>Susu</b>
            <a>sux</a>
            <b>Sumerian</b>
            <a>swa</a>
            <b>Swahili</b>
            <a>swe</a>
            <b>Swedish</b>
            <a>syc</a>
            <b>Classical Syriac</b>
            <a>syr</a>
            <b>Syriac</b>
            <a>tah</a>
            <b>Tahitian</b>
            <a>tai</a>
            <b>Tai</b>
            <a>tam</a>
            <b>Tamil</b>
            <a>tat</a>
            <b>Tatar</b>
            <a>tel</a>
            <b>Telugu</b>
            <a>tem</a>
            <b>Timne</b>
            <a>ter</a>
            <b>Tereno</b>
            <a>tet</a>
            <b>Tetum</b>
            <a>tgk</a>
            <b>Tajik</b>
            <a>tgl</a>
            <b>Tagalog</b>
            <a>tha</a>
            <b>Thai</b>
            <a>tib</a>
            <b>Tibetan</b>
            <a>tig</a>
            <b>Tigre</b>
            <a>tir</a>
            <b>Tigrinya</b>
            <a>tiv</a>
            <b>Tiv</b>
            <a>tkl</a>
            <b>Tokelau</b>
            <a>tlh</a>
            <b>Klingon tlhIngan-Hol</b>
            <a>tli</a>
            <b>Tlingit</b>
            <a>tmh</a>
            <b>Tamashek</b>
            <a>tog</a>
            <b>Tonga (Nyasa)</b>
            <a>ton</a>
            <b>Tonga (Tonga Islands)</b>
            <a>tpi</a>
            <b>Tok Pisin</b>
            <a>tsi</a>
            <b>Tsimshian</b>
            <a>tsn</a>
            <b>Tswana</b>
            <a>tso</a>
            <b>Tsonga</b>
            <a>tuk</a>
            <b>Turkmen</b>
            <a>tum</a>
            <b>Tumbuka</b>
            <a>tup</a>
            <b>Tupi</b>
            <a>tur</a>
            <b>Turkish</b>
            <a>tut</a>
            <b>Altaic</b>
            <a>tvl</a>
            <b>Tuvalu</b>
            <a>twi</a>
            <b>Twi</b>
            <a>tyv</a>
            <b>Tuvinian</b>
            <a>udm</a>
            <b>Udmurt</b>
            <a>uga</a>
            <b>Ugaritic</b>
            <a>uig</a>
            <b>Uighur Uyghur</b>
            <a>ukr</a>
            <b>Ukrainian</b>
            <a>umb</a>
            <b>Umbundu</b>
            <a>und</a>
            <b>Undetermined</b>
            <a>urd</a>
            <b>Urdu</b>
            <a>uzb</a>
            <b>Uzbek</b>
            <a>vai</a>
            <b>Vai</b>
            <a>ven</a>
            <b>Venda</b>
            <a>vie</a>
            <b>Vietnamese</b>
            <a>vol</a>
            <b>Volapük</b>
            <a>vot</a>
            <b>Votic</b>
            <a>wak</a>
            <b>Wakashan</b>
            <a>wal</a>
            <b>Wolaitta Wolaytta</b>
            <a>war</a>
            <b>Waray</b>
            <a>was</a>
            <b>Washo</b>
            <a>wel</a>
            <b>Welsh</b>
            <a>wen</a>
            <b>Sorbian</b>
            <a>wln</a>
            <b>Walloon</b>
            <a>wol</a>
            <b>Wolof</b>
            <a>xal</a>
            <b>Kalmyk Oirat</b>
            <a>xho</a>
            <b>Xhosa</b>
            <a>yao</a>
            <b>Yao</b>
            <a>yap</a>
            <b>Yapese</b>
            <a>yid</a>
            <b>Yiddish</b>
            <a>yor</a>
            <b>Yoruba</b>
            <a>ypk</a>
            <b>Yupik</b>
            <a>zap</a>
            <b>Zapotec</b>
            <a>zbl</a>
            <b>Blissymbols Blissymbolics Bliss</b>
            <a>zen</a>
            <b>Zenaga</b>
            <a>zgh</a>
            <b>Tamazight</b>
            <a>zha</a>
            <b>Zhuang Chuang</b>
            <a>znd</a>
            <b>Zande</b>
            <a>zul</a>
            <b>Zulu</b>
            <a>zun</a>
            <b>Zuni</b>
            <a>zza</a>
            <b>Zaza</b>
        </lang>
    </xsl:variable>

</xsl:stylesheet>
