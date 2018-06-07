<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim
    http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" version="2.0"
    exclude-result-prefixes="marc xs xsi">
    <xsl:output method="xml" exclude-result-prefixes="#all"/>
    
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

<!--    remove letters except s and most punct from dates -->
    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='f']">
        <xsl:copy>
            <xsl:attribute name="code">f</xsl:attribute>
            <xsl:value-of select="translate(., 'abcdefghijklmnopqrtuvqxyz()[].,:' ,'')"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='g']">
        <xsl:copy>
            <xsl:attribute name="code">g</xsl:attribute>
            <xsl:value-of select="translate(., 'abcdefghijklmnopqrtuvqxyz()[].,:' ,'')"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- remove ending periods everywhere   -->    
    <xsl:template
        match="marc:datafield/marc:subfield/text()[ends-with(., '.')]">
        <xsl:variable name="s" select="." />
        <xsl:value-of select="substring($s, 1, string-length($s) - 1)" />
    </xsl:template>
    
    <xsl:template match="marc:datafield[@tag='555'][2]">
        
<!--        copy nothing, since the 2nd 555 was aleady copied to the first using the previous stylesheet -->
    </xsl:template>
    
    <xsl:template match="marc:datafield[@tag='856'][marc:subfield[@code='u']/contains(., 'services/preservation')]">
        
        <!--        copy nothing, because we want to get rid of this 856 -->
    </xsl:template>
    
    
</xsl:stylesheet>