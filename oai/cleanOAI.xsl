<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs marc" version="2.0">
    <!--  this stylesheet will take OAI marc records from the Columbia University Libraries ArchivesSpace instance and clean them up for Voyager import.  -->
    
 <xsl:output indent="yes"/>
 
<!--    <xsl:param name="from_time"><xsl:value-of select="current-dateTime() - xs:dayTimeDuration('P1DT2H')"/></xsl:param>
-->

<!-- Default offset is 30 hours before current time. All records with datestamp after this time will be captured. Send a different time value as param from_time to change. -->

    
    <!-- $cutoff_date param: Only provide if want to override the relative offset with an absolute dateTime value in ISO format, e.g., 2020-01-21T16:32:21Z or  2020-03-25T19:27:22.169-04:00. If not provided, will rely on $time_offset param. -->
    <xsl:param name="cutoff_date"/>
 
 
    <!-- $time_offset param: Pass to stylesheet in xs:dayTimeDuration format (P{days}DT{hours}H). If none, will use the default value defined below -->
    <xsl:param name="time_offset">P0DT24H</xsl:param>
    
    <xsl:variable name="from_time">
        <!-- if there is a specific cutoff date provided use that, otherwise subtract the offset from current dateTime. -->
        <xsl:choose>
            <xsl:when test="normalize-space($cutoff_date)">
                <xsl:value-of select="$cutoff_date"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="current-dateTime() - xs:dayTimeDuration($time_offset)"/>
            </xsl:otherwise>
        </xsl:choose>        
    </xsl:variable>
    
    <xsl:variable name="theDateTime"><xsl:value-of select="current-dateTime()"/></xsl:variable>
    
    

    <xsl:variable name="lf"><xsl:text>&#x0A;</xsl:text></xsl:variable>
 
 
 
    <!--  The initial match kicks of a loop that ignores the OAI XML apparatus -->
    
    <xsl:template match="/">
        
        <!-- TEST -->
            

            
       <xsl:message>  
           <xsl:text>Time of execution: </xsl:text>
           <xsl:value-of select="$theDateTime"/>
           <xsl:value-of select="$lf"/>
       </xsl:message>
        
        <xsl:message>
            <xsl:text>cut-off datetime: </xsl:text>
            <xsl:value-of select="$from_time"/>
            <xsl:value-of select="$lf"/>
       </xsl:message>
        <!-- Output record count to stdout -->
        <xsl:message>

            <xsl:value-of select="$lf"/>
            <xsl:text>Count of records processed: </xsl:text>
            <xsl:value-of select="count( repository/record[contains(header/identifier, '/resources/')  and header/datestamp >= $from_time])"></xsl:value-of>
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
        <xsl:if test="contains(header/identifier, '/resources/') and header/datestamp >= $from_time">
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
       <!-- <xsl:copy/> -->
        <xsl:call-template name="cleanText">
            <xsl:with-param name="theText"><xsl:value-of select="."/></xsl:with-param>
        </xsl:call-template>
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
                        <xsl:apply-templates select="marc:subfield[@code='c']/text()"/>
                    </xsl:otherwise>
                </xsl:choose>
            </subfield>
            <subfield code="e">
                <xsl:apply-templates select="marc:subfield[@code = 'e']/text()"/>
            </subfield>
        </datafield>
        
     </xsl:template>

    <!--    If there are 041 with empty subfields AND there are no 546 languages to parse, delete -->
    <xsl:template
        match="marc:datafield[@tag = '041'][marc:subfield[not(normalize-space(text()))]][../not(marc:datafield[@tag = '546'])]">
            <!-- Do nothing -->
    </xsl:template>

  
    

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
                <xsl:apply-templates select="marc:subfield[@code='u']/text()"/>    
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
        
  
    

    <!--    reorder elements -->
    <!-- Grab the record, copy the leader and sort the control and data fields. -->
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
        <record>
            <xsl:element name="leader">
                <xsl:value-of select="marc:leader"/>
            </xsl:element>
            <!--           for prod, move 099 to 001 -->
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">001</xsl:attribute>
                <xsl:apply-templates select="marc:datafield[@tag = '099']/marc:subfield[@code = 'a']/text()"/>
            </xsl:element>
            <!--         added 003 to allow for creation of 035 upon import   -->
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">003</xsl:attribute>
                <xsl:text>NNC</xsl:text>
            </xsl:element>
            <xsl:element name="controlfield">
                <xsl:attribute name="tag">008</xsl:attribute>
                <xsl:apply-templates select="marc:controlfield/text()"/>
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
