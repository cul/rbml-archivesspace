<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs marc" version="2.0">
    <!--  this stylesheet will take OAI marc records from the Columbia University Libraries ArchivesSpace instance and clean them up for Voyager import.  -->
    
 <xsl:output indent="yes"/>
    
    
    
    <xsl:variable name="theDateTime"><xsl:value-of select="current-dateTime()"/></xsl:variable>
    
    
    
    <xsl:variable name="lf"><xsl:text>&#x0A;</xsl:text></xsl:variable>
    
    
    
    <!--  The initial match kicks off a loop that ignores the OAI XML apparatus -->
    
    <xsl:template match="/">
              
        <xsl:message>  
            <xsl:text>Time of execution: </xsl:text>
            <xsl:value-of select="$theDateTime"/>
            <xsl:value-of select="$lf"/>
        </xsl:message>
        
        <!-- Output record count to stdout -->
        <xsl:message>
            
            <xsl:value-of select="$lf"/>
            <xsl:text>Count of records processed: </xsl:text>
            <xsl:value-of select="count( repository/record[contains(header/identifier, '/resources/')])"></xsl:value-of>
            <xsl:value-of select="$lf"/>
        </xsl:message>
        
        
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
    
    
    
    <!--    Assemble elements in the correct order. -->

    <xsl:template match="marc:record">   
        <!-- output some info to saxon text stream -->
        <xsl:message>
            <xsl:value-of select="marc:datafield[@tag='099']/marc:subfield[@code='a']"/>
            <xsl:text>: </xsl:text>
            <xsl:value-of select="marc:datafield[@tag='245']/marc:subfield[@code='a']"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="ancestor::record/header/datestamp"/>
            <xsl:text>) </xsl:text>
        </xsl:message>        
        
        <!-- Save the repo code. -->
        <xsl:variable name="repo"><xsl:value-of select="replace(ancestor::record/header/identifier, '^.*?repositories/(\d)/.*?$','$1')"></xsl:value-of></xsl:variable>
        
        <record>
            <xsl:variable name="dataFields">
                <!-- This variable tree assembles all datafield elements for inclusion. They are sorted by @tag when invoked. -->
                <xsl:apply-templates select="marc:datafield"/>
                
                <!-- RBMLBOOKS  -->
                <!-- Some add-ins only for RBMLBOOKS -->
                <xsl:if test="$repo = '6'">
                    <datafield ind1=" " ind2=" " tag='336'>
                        <subfield code='a'>text</subfield>
                        <subfield code='b'>txt</subfield>
                        <subfield code='2'>rdacontent</subfield>
                    </datafield>
                    <datafield ind1=" " ind2=" " tag='337'>
                        <subfield code='a'>unmediated</subfield>
                        <subfield code='b'>n</subfield>
                        <subfield code='2'>rdamedia</subfield>                    
                    </datafield>
                    <datafield ind1=" " ind2=" " tag='338'>
                        <subfield code='a'>volume</subfield>
                        <subfield code='b'>nc</subfield>
                        <subfield code='2'>rdacarrier</subfield>
                    </datafield>
                </xsl:if>
                <!-- END RBMLBOOKS  -->
            </xsl:variable>
            
            <xsl:choose>
                <!-- RBMLBOOKS  -->
                <xsl:when test="$repo = '6'">
                    <leader>00000cac a22000707i 4500</leader>
                </xsl:when>
                <!-- END RBMLBOOKS  -->
                <xsl:otherwise>
                    <leader>
                        <xsl:value-of select="marc:leader"/>
                    </leader>                    
                </xsl:otherwise>
            </xsl:choose>
            
            <!--           for prod, move 099 to 001 -->
            <controlfield tag='001'>
                <xsl:apply-templates select="marc:datafield[@tag = '099']/marc:subfield[@code = 'a']/text()"/>
            </controlfield>
            
            <xsl:choose>
                <!-- RBMLBOOKS  -->
                <xsl:when test="contains(ancestor::record/header/identifier, 'repositories/6')">
                    <controlfield tag='008'>
                        <!-- Test if there are only bulk dates, and change pos 6 to k if so; -->
                        <!-- otherwise leave as inclusive ('i') dates. -->
                        <xsl:choose>
                            <xsl:when test="marc:datafield[@tag='245']/marc:subfield[@code='g']
                                and 
                                not(marc:datafield[@tag='245']/marc:subfield[@code='f'])">
                                <xsl:value-of select="replace(substring(marc:controlfield[@tag='008'], 1, 7), 'i', 'k')"/>
                            </xsl:when>
                            <xsl:otherwise><xsl:value-of select="substring(marc:controlfield[@tag='008'],1,7)"/></xsl:otherwise>
                        </xsl:choose>
                       
                        <xsl:value-of select="replace(substring(marc:controlfield[@tag='008'], 8),'xxu','vp')"/>
                        <!--<xsl:value-of select="replace(marc:controlfield[@tag='008'],'xxu','vp')"/>-->
                    </controlfield>
                </xsl:when>
                <!-- END RBMLBOOKS  -->
                
                <xsl:otherwise>
                    <!--         added 003 to allow for creation of 035 upon import   -->
                    <controlfield tag='003'>NNC</controlfield>
                    <controlfield tag='008'>
                        <xsl:value-of select="marc:controlfield[@tag='008']"/>
                    </controlfield>
                </xsl:otherwise>
            </xsl:choose>
          
            
            <!-- Insert all datafields saved in the variable $dataFields, sorted by tag order. -->
            <xsl:for-each select="$dataFields/datafield">
                <xsl:sort select="@tag"/>
                <xsl:copy-of select="."/>
            </xsl:for-each>
            
        </record>
        
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
       <!-- <xsl:copy/> -->
        <xsl:call-template name="cleanText">
            <xsl:with-param name="theText"><xsl:value-of select="."/></xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    <!--    end three templates     -->


    <!-- RBMLBOOKS  -->

    <xsl:template match="marc:datafield[@tag= ('044',  '049', '852')][contains(ancestor::record/header/identifier, 'repositories/6')]">
        <!--   remove these fields  -->
    </xsl:template>

    
    <xsl:template match="marc:datafield[@tag= '300'][contains(ancestor::record/header/identifier, 'repositories/6')]">
        <datafield ind1='{@ind1}' ind2='{@ind2}' tag='300'>
            <subfield code='a'>
            <!-- Concatenate 300 subfields into one string -->
            <xsl:value-of select="string-join(marc:subfield, ' ')"/>
            </subfield>           
        </datafield>
    </xsl:template>
    
    <!--   Omit 099   -->
    <xsl:template match="marc:datafield[@tag='099'][contains(ancestor::record/header/identifier, 'repositories/6')]">
    </xsl:template>
   
   
        <!--   Omit 035 if has only bibid w no prefix    -->
        <!--   (Cancelling this per kws convo 1/22/21.)       -->
<!--
     <xsl:template match="marc:datafield[@tag='035'][marc:subfield][contains(ancestor::record/header/identifier, 'repositories/6')]">
        <xsl:if test="not(matches(marc:subfield[@code='a'], '^\d+$'))">
            
            <datafield ind1="{@ind1}" ind2="{@ind2}" tag="035">
                <xsl:apply-templates/>
            </datafield>
        </xsl:if>
    </xsl:template>
   -->


    <xsl:template match="marc:datafield[starts-with(@tag,'1')][contains(ancestor::record/header/identifier, 'repositories/6')]">
        <datafield ind1="{@ind1}" ind2="{@ind2}" tag="7{substring(@tag,2,2)}">
            <xsl:apply-templates/>
        </datafield>
        
    </xsl:template>
    



    <!-- END RBMLBOOKS  -->


    <!--  remove elements without content (extra 035 and 040s etc being exported by AS for some reason) -->
    <xsl:template match="marc:datafield[not(marc:subfield)]">
        <!--        do nothing  -->
    </xsl:template>
    
    <!--   remove "empty" subfields having no text content --> 
    <xsl:template match="marc:subfield[not(normalize-space(text()))]">
        <!--        do nothing  -->
    </xsl:template>


    <!-- NOT RBMLBOOKS -->
    
    <!--    reformat 035 CULASPC to local practice, add NNC 035 field -->
    <!--    commented out second test, no longer applicable for dupe NNC 035s: added test for adjacent silbing with 035 containing NNC; if exists, do nothing. If not, create.    -->
    <!--  see below, added a control field 003 to allow for proper 035 building upon ingest into voyager  -->
    <xsl:template match="marc:datafield[@tag = '035'][marc:subfield[contains(., 'CULASPC')]][not(contains(ancestor::record/header/identifier, 'repositories/6'))]">
        <datafield ind1=" " ind2=" " tag="035">
            <subfield code="a">
                <xsl:text>(NNC)CULASPC:voyager:</xsl:text>
                <xsl:value-of select="normalize-space(substring-after(., '-'))"/>
            </subfield>
        </datafield>
    </xsl:template>


    <!--  add repo to 040 field; test for UA in 852$j  -->
    <xsl:template match="marc:datafield[@tag = '040'][marc:subfield] [not(contains(ancestor::record/header/identifier, 'repositories/6'))]">

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
                        <xsl:apply-templates select="marc:subfield[@code='c']/text()"/>
                    </xsl:otherwise>
                </xsl:choose>
            </subfield>
            <xsl:if test="marc:subfield[@code = 'e']">
                   <xsl:apply-templates select="marc:subfield[@code = 'e']"/>
            </xsl:if>
        </datafield>
        
     </xsl:template>

    <!-- END NOT RBMLBOOKS -->


    <!-- RBMLBOOKS   -->
    <xsl:template match="marc:datafield[@tag = '040']/marc:subfield[@code=('a','c')] [contains(ancestor::record/header/identifier, 'repositories/6')]">
        <subfield code='{@code}'>NNC</subfield>        
    </xsl:template>
    <!-- END RBMLBOOKS   -->
    

    <!--    If there are 041 with empty subfields AND there are no 546 languages to parse, delete -->
    <xsl:template
        match="marc:datafield[@tag = '041'][marc:subfield[not(normalize-space(text()))]][../not(marc:datafield[@tag = '546'])]">
            <!-- Do nothing -->
    </xsl:template>

 
 
    <!-- RBMLBOOKS --> 
    <xsl:template match="marc:datafield[@tag = '245'][contains(ancestor::record/header/identifier, 'repositories/6')]">
        <datafield ind1='{@ind1}' ind2='{@ind2}' tag='245'>
            <xsl:apply-templates select="marc:subfield[not(@code = ('g','f'))]"/>
        </datafield>
        
        <xsl:if test="marc:subfield[@code='g'] or marc:subfield[@code='f']">
            <datafield ind1=' ' ind2='1' tag='264'>
            <xsl:for-each select="marc:subfield[@code='f'] | marc:subfield[@code='g']">
                <subfield code='c'><xsl:value-of select='normalize-space(.)'/></subfield>
            </xsl:for-each>
        </datafield>
        </xsl:if>
    </xsl:template>
    
    <!-- END RBMLBOOKS --> 

    <!--  add "bulk" in front of 245 $g field  -->
    <xsl:template match="marc:datafield[@tag = '245']/marc:subfield[@code = 'g']">
        <subfield code="g">
            <xsl:text>bulk </xsl:text>
            <xsl:apply-templates select="text()"/>
        </subfield>
    </xsl:template>
    
    <!--  add 1st indicator 1 to 544 related materials  -->
    <xsl:template match="marc:datafield[@tag = '544']">
        <datafield ind1="1" ind2=" " tag="544">
        <subfield code="d">
            <xsl:apply-templates select="marc:subfield[@code='d']/text()"/>
        </subfield>
        </datafield>
    </xsl:template>
 
 
    <!-- ONLY FOR NON-RBMLBOOKS -->

    <!--  remove subfield e from 1XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '1')]]/marc:subfield[@code = 'e'] [not(contains(ancestor::record/header/identifier, 'repositories/6'))]">
        <!--     do nothing   -->
    </xsl:template>

    <!--  remove subfield e from 6XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '6')]]/marc:subfield[@code = 'e'] [not(contains(ancestor::record/header/identifier, 'repositories/6'))]">
        <!--     do nothing   -->
    </xsl:template>

    <!--  remove subfield e from 7XX  -->

    <xsl:template match="marc:datafield[@tag[starts-with(., '7')]]/marc:subfield[@code = 'e'] [not(contains(ancestor::record/header/identifier, 'repositories/6'))]">
        <!--     do nothing   -->
    </xsl:template>
    

    <!--  remove subfield 0 from 6XX when there are subject subdivisions ($v, $x, $y, $z)  -->
    
    <xsl:template match="marc:datafield[@tag[starts-with(., '6')]]/marc:subfield[@code = '0'][../marc:subfield/@code[contains('vxyz',.)]] [not(contains(ancestor::record/header/identifier, 'repositories/6'))]">
             <!--     do nothing   -->
    </xsl:template>
    
    <!-- END NON-RBMLBOOKS -->
    

<!--  add $3 "Finding aid" to 856 fields -->
    <xsl:template match="marc:datafield[@tag = '856']">
        
        <!-- NOT RBMLBOOKS -->
        <xsl:if test="not(contains(ancestor::record/header/identifier, 'repositories/6'))">
        <datafield ind1="4" ind2="2" tag="856">
            <subfield code="u">
                <xsl:apply-templates select="marc:subfield[@code='u']/text()"/>    
            </subfield>
            <!--<subfield code="z">
                <xsl:value-of select="marc:subfield[@code='z']"/>
            </subfield>-->
            <subfield code="3">
                <xsl:text>Finding aid</xsl:text>
            </subfield>
        </datafield>
        </xsl:if>
        <!-- END NOT RBMLBOOKS -->
        
    </xsl:template>

    <!-- For corporate names (110 and 610), remove trailing comma if no subordinate name available. -->
    <xsl:template match="marc:datafield[@tag = '110' or @tag = '610']/marc:subfield[@code='a']">
        <subfield code="a">
            <xsl:choose>
                <xsl:when test="../marc:subfield[@code='b']">
                    <!--  there is a $b following, keep punctuation   -->
                    <xsl:apply-templates select="text()"/>  
                </xsl:when>
                <xsl:otherwise>
                    <!--  there is no $b following, strip punctuation   -->
                    <xsl:call-template name="stripPunctuation"/>
                </xsl:otherwise>
            </xsl:choose>
        </subfield>
    </xsl:template>
      

    <!-- For 110$b and 610$b, remove trailing comma. -->
    <xsl:template match="marc:datafield[@tag = '110' or @tag = '610']/marc:subfield[@code='b']">
        <subfield code="b">
            <xsl:choose>
                <xsl:when test="following-sibling::marc:subfield[@code='b']">
<!--                    <xsl:call-template name="fullStop"/> -->
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="stripPunctuation"/>
                </xsl:otherwise>
            </xsl:choose>
        </subfield>
    </xsl:template>
        
  
    
    
    <!--    remove colons from beginning of fields -->
    <xsl:template match="marc:subfield[starts-with(., ':')]">
        <subfield code='{@code}'>
            <xsl:copy-of select="normalize-space(translate(., ':', ''))"/>
        </subfield>
    </xsl:template>

    <!--    remove commas from end of sub field d -->
    <xsl:template match="marc:subfield[@code = 'd']">
        <subfield code="d">
            <xsl:call-template name="stripPunctuation"/>
        </subfield>
    </xsl:template>
    
    
    
    <!-- Strip trailing comma from specified text nodes  -->
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
    
    <!-- Strip trailing punctuation from specified text nodes  -->
    <xsl:template name="stripPunctuation">
        <xsl:analyze-string select="normalize-space(.)" regex="^(.*?)([,\.]+)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select='.'/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>
    
    
    <!-- Replace trailing punctuation with a period. -->
    <xsl:template name="fullStop">
        <xsl:analyze-string select="normalize-space(.)" regex="^(.*?)([,\.]+)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/><xsl:text>.</xsl:text>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select='.'/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>
    
    
    <!-- Strip trailing punctuation from specified text nodes  -->
    <xsl:template name="trimPunctuation">
        <xsl:analyze-string select="normalize-space(.)" regex="^(.*?)([,\.]+)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
                <xsl:value-of select="substring(regex-group(2),1,1)"/>
                
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select='.'/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>
    
    
    <xsl:template name="cleanText">
        <xsl:param name="theText"/>
        <xsl:analyze-string select="$theText" regex="([—–…])">
            <xsl:matching-substring>
                <xsl:choose>
                    <xsl:when test="regex-group(1) = '—'">
                     <xsl:text>--</xsl:text>
                    </xsl:when>
                    <xsl:when test="regex-group(1) = '–'">
                        <xsl:text>-</xsl:text>
                    </xsl:when>
                    <xsl:when test="regex-group(1) = '…'">
                        <xsl:text>...</xsl:text>
                    </xsl:when>
                </xsl:choose>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <xsl:value-of select="."/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>
    

</xsl:stylesheet>
