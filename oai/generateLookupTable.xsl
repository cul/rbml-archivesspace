<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs marc" version="2.0">
    <!-- Run this against a full OAI harvest to generate a lookup table (repo,asid,bibid)-->

    <xsl:output indent="no" method="text"/>

    <!--  This is where the column heads are drawn from. Should match process below.   -->
    <xsl:variable name="myHead">REPO,ASID,BIBID</xsl:variable>

    <xsl:variable name="lf">
        <xsl:text>
</xsl:text>
    </xsl:variable>

    <xsl:variable name="delim1">,</xsl:variable>


    <xsl:template match="/">
        <xsl:value-of select="$myHead"/>
        <xsl:value-of select="$lf"/>

        <xsl:apply-templates select="repository/record[contains(header/identifier, '/resources/')]"
        />
    </xsl:template>


    <xsl:template match="record">
        <xsl:analyze-string select="header/identifier" regex="^.*repositories/(.*)/resources/(.*)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="regex-group(2)"/>
             </xsl:matching-substring>
        </xsl:analyze-string>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of
            select="metadata/marc:collection/marc:record/marc:datafield[@tag='099']/marc:subfield[@code='a']"/>
        <xsl:value-of select="$lf"/>


    </xsl:template>


</xsl:stylesheet>
