<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs marc"
    version="2.0">
<!--  this stylesheet will take OAI marc records from the Columbia University Libraries ArchivesSpace instance and clean them up for Voyager import. v2 KS 2018-06-19  -->
<!--  The initial match kicks of a loop that ignores the OAI XML apparatus -->
   <xsl:template match="/">
       <collection>
       <xsl:for-each select="repository/record/metadata/marc:collection/marc:record">
           <xsl:apply-templates select="."/>
       </xsl:for-each>
       </collection>
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
    
<!--    reformat 035 CULASPC to local practice, add NNC 035 field -->
    <xsl:template match="marc:datafield[@tag='035'][marc:subfield[contains(., 'CULASPC')]]">
        <datafield ind1=" " ind2=" " tag="035">
            <subfield code="a">
                <xsl:text>(CULASPC)</xsl:text>
                <xsl:value-of select="substring-after(., '-')"/>
            </subfield>
        </datafield>  
        <datafield ind1=" " ind2=" " tag="035">
            <subfield code="a">
                <xsl:text>(NNC)</xsl:text>
                <xsl:value-of select="substring-after(., '-')"/>
            </subfield>
        </datafield>
    </xsl:template>
    
<!--  add repo to 040 field; test for UA in 852$j  -->
    <xsl:template match="marc:datafield[@tag='040'][marc:subfield]">
        <datafield ind1=" " ind2=" " tag="040">
            <xsl:variable name="fortyText">
                <xsl:text>NNC-</xsl:text>
                <xsl:choose>
                    <xsl:when test="../marc:datafield[@tag='852']/marc:subfield[@code='j'][contains(., 'UA')]">
                        <xsl:text>UA</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <!-- grab repository code from 852               -->
                        <xsl:value-of select="../marc:datafield[@tag='852']/marc:subfield[@code='b']"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <subfield code="a">
                <xsl:value-of select="$fortyText"></xsl:value-of>
            </subfield>
            <subfield code="c">
                <xsl:value-of select="$fortyText"></xsl:value-of>
            </subfield>
            <subfield code="e">
            <xsl:value-of select="marc:subfield[@code='e']"/>
            </subfield>
        </datafield>  
    </xsl:template>
    
<!--  once repositories are input into AS, look at 852 and modify as needed  -->
    
<!--    reorder elements -->
    <!-- Grab the record, copy the leader and sort the control and data fields. -->
    <xsl:template match="marc:record">
        <record>
        <xsl:element name="leader">
            <xsl:value-of select="marc:leader"/>
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
        <xsl:copy-of select="translate(., ':', '')"/>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>
