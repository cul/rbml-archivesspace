<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0"
    xpath-default-namespace="urn:isbn:1-931666-22-9">
    <!-- Use to transform AS-exported EADs to CUL-compatible EAD for finding aid publication. See ASI-112. -->

    <xsl:output indent="yes" method="xml"/>

    <!-- Schema relative path.   -->
    <xsl:param name="theSchemaURL">../schema/ead_cul.nvdl</xsl:param>

    <!-- Identify the repo (e.g., nnc-rb) for later use. -->
    <xsl:variable name="repo"
        select="lower-case(substring-after(ead/eadheader/eadid/@mainagencycode, '-'))"/>


    <!---->

    <!-- Identity template -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/">
        <!-- Add header to point to NVDL for validation.  -->
        <xsl:processing-instruction name="xml-model">
href="<xsl:value-of select="$theSchemaURL"/>" type="application/xml" schematypens="http://purl.oclc.org/dsdl/nvdl/ns/structure/1.0" phase="ALL" title="CUL NVDL schema"</xsl:processing-instruction>
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template match="eadheader">
        <xsl:copy>
            <!-- TODO: Get publish status dynamically.     -->
            <xsl:attribute name="findaidstatus">publish</xsl:attribute>
            <xsl:apply-templates select="./@*"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="ead">
        <ead xmlns="urn:isbn:1-931666-22-9" xmlns:xlink="http://www.w3.org/1999/xlink"
            audience="external">
            <xsl:apply-templates/>
        </ead>
    </xsl:template>

    <xsl:template match="did/unitid">
        <unitid xmlns="urn:isbn:1-931666-22-9" encodinganalog="090$b" countrycode="US"
            repositorycode="nnc-rb" type="call_num">{CALL NUMBER GOES HERE}</unitid>
        <unitid xmlns="urn:isbn:1-931666-22-9" encodinganalog="001" countrycode="US"
            repositorycode="{$repo}" type="clio">
            <xsl:apply-templates/>
        </unitid>
    </xsl:template>

    <xsl:template match="did/langmaterial">
        <xsl:choose>
            <xsl:when test="count(../langmaterial)>1">
                <xsl:if test="not(language[@langcode])">
                    <xsl:copy>
                        <xsl:apply-templates select="@*"/>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
