<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ead="urn:isbn:1-931666-22-9"
    xmlns:xlink="http://www.w3.org/1999/xlink" xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="text"/>

    <!--    Stylesheet to extract relevant info from an EAD for QC. -->


    <!--    set this to "Y" to generate the head for spreadsheet. -->
    <xsl:param name="header"/>


    <xsl:variable name="lf">
        <xsl:text>
</xsl:text>
    </xsl:variable>

    <xsl:variable name="delim1">|</xsl:variable>
    <xsl:variable name="delim2">;</xsl:variable>



    <!--    This is where the column heads are drawn from. Should match process below.   -->
    <xsl:variable name="myHead"
        >BIBID|Title|Repo|CountArchdesc|CountDSC|CountContainers|CountDSCChars|ContainerMaxDepth|ArchdescUnique|DSCUnique</xsl:variable>




    <!--    If param is set header=info, then output the defined header; otherwise, process all tags. -->
    <!--    Call this first from script, and then cycle through a set of files to generate rows. -->
    <xsl:template match="/">
        <xsl:choose>
            <xsl:when test="$header='Y'">
                <xsl:value-of select="$myHead"/>
                <xsl:value-of select="$lf"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="ead:ead"/>

            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="ead:ead">

        <!--
        <xsl:value-of select="$myHead"/>
        <xsl:value-of select="$lf"/>
-->



        <!--            BibID -->
        <xsl:value-of select="archdesc/did/unitid[1]"/>
        <xsl:value-of select="$delim1"/>

        <!--            Title -->
        <xsl:value-of select="normalize-space(archdesc/did/unittitle[1])"/>
        <xsl:value-of select="$delim1"/>


        <!--            Repo -->

        <xsl:value-of select="eadheader/eadid[1]/@mainagencycode"/>
        <xsl:value-of select="$delim1"/>

        <!--            Count of archdesc elements (not dsc) -->
        <xsl:value-of select="count(archdesc/descendant::*[not(ancestor-or-self::dsc)])"/>
        <xsl:value-of select="$delim1"/>

        <!--            Count of dsc descendents -->
        <xsl:value-of select="count(archdesc/dsc/descendant::*)"/>
        <xsl:value-of select="$delim1"/>

        <!--            Count of containers -->
        <xsl:value-of select="count(//c)"/>
        <xsl:value-of select="$delim1"/>


        <!--            Count of dsc chars -->
        <xsl:value-of
            select="sum(archdesc/dsc/descendant-or-self::text()/string-length(normalize-space(.)))"/>
        <xsl:value-of select="$delim1"/>


        <!--        Max container depth below dsc -->
        <xsl:value-of select="max(//c/count(ancestor::node())) - 3"/>
        <xsl:value-of select="$delim1"/>


        
        <!--     List of unique elements in archdesc   -->
        <xsl:for-each select="distinct-values(archdesc//*[not(ancestor::dsc)]/local-name())">
            <xsl:sort select="."/>
            <xsl:value-of select="."/>
            <xsl:text>;</xsl:text>
        </xsl:for-each>

        <xsl:value-of select="$delim1"/>
        
        <!--     List of unique elements in dsc   -->
        <xsl:for-each select="distinct-values(archdesc/dsc//*/local-name())">
            <xsl:sort select="."/>
            <xsl:value-of select="."/>
            <xsl:text>;</xsl:text>
        </xsl:for-each>
        
       

        <xsl:value-of select="$lf"/>



    </xsl:template>




</xsl:stylesheet>
