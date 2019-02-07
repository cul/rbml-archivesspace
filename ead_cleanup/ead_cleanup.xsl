<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="xml" encoding="utf-8" indent="yes"/>


    <!-- Source will be output from ead_merge.xsl -->


    <xsl:param name="theDate">
        <xsl:value-of select="format-date(current-date(), 
            '[Y0001]-[M01]-[D01]')"/>
    </xsl:param>



    <!-- Identity template -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/">
        <!-- Some info about merge added at runtime.    -->
        <xsl:comment> 
    <xsl:text>File cleaned on  </xsl:text>
    <xsl:value-of select="current-dateTime()"/>
        </xsl:comment>
        <xsl:text>&#xa;</xsl:text>

        <xsl:apply-templates/>

    </xsl:template>



    <!-- Minor fix to malformed URLs in data -->
    <xsl:template match="eadid/@url">
        <xsl:attribute name="url">
            <xsl:analyze-string select="." regex="/ead//">
                <xsl:matching-substring>/ead/</xsl:matching-substring>
                <xsl:non-matching-substring>
                    <xsl:value-of select="."/>
                </xsl:non-matching-substring>
            </xsl:analyze-string>
        </xsl:attribute>
    </xsl:template>


    <!--Add revision note for current process. -->
    <xsl:template match="revisiondesc">
        <xsl:copy>
            <xsl:apply-templates/>
            <change xmlns="urn:isbn:1-931666-22-9">
                <date normal="{$theDate}">
                    <xsl:value-of select="$theDate"/>
                </date>
                <item>EAD was imported spring 2019 as part of the ArchivesSpace Phase II
                    migration.</item>
            </change>
        </xsl:copy>
    </xsl:template>



    <xsl:template match="titleproper[ancestor::eadheader]/num">
        <!-- omit -->
    </xsl:template>


    <!--   fix malformed @source attributes in persname, geogname, subject, etc. -->
    <xsl:template match="@source">
        <xsl:choose>
            <xsl:when test=".='Library of Congress Subject Headings'">
                <xsl:attribute name="source">lcsh</xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                <xsl:attribute name="source" select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-- Fix error where scopecontent note is duplicated in archdesc/odd and archdesc/scopecontent. -->
    <xsl:template match="odd[parent::archdesc][contains(head,'Scope and content')]">
        <xsl:choose>
            <xsl:when test="//archdesc/scopecontent">
                <!-- omit -->
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-- strip trailing commas from unittitle  -->
    <!-- TODO: refine this to retain child elements while stripping comma at end. See ASI-94. -->
    <!-- 
    <xsl:template match="unittitle[ancestor::dsc]">
        <xsl:copy>
            <xsl:call-template name="stripComma"/>
        </xsl:copy>
    </xsl:template>
-->


    <!-- delete @audience=internal attributes -->
    <xsl:template match="//c/@audience[.='internal']"/>


    <!--  Omit ids from containers-->
    <xsl:template match="c/@id"/>

    <!-- Convert all container/@type to lowercase -->
    <xsl:template match="container/@type">
        <xsl:attribute name="type">
            <xsl:value-of select="lower-case(.)"/>
        </xsl:attribute>

    </xsl:template>



    <!-- Delete empty elements that won't import well -->

    <xsl:template match="scopecontent[not(normalize-space(.))][not(normalize-space(p))][not(@*)]"/>

    <xsl:template match="physdesc[not(normalize-space(.))][not(normalize-space(extent))][not(@*)]"/>

    <xsl:template match="unitdate[not(normalize-space(.))][not(@*)]"/>

    <xsl:template
        match="lb[not(normalize-space(.))] | genreform[not(normalize-space(.))] | physdesc[not(normalize-space(.))]"/>


    <!-- empty p tags  -->
    <xsl:template match="p[not(normalize-space(.))][not(@*)][not(ancestor::dsc)]"/>


    <!-- Strip trailing punctuation from specified text nodes  -->
    <!--    TODO: fix this! -->
    <xsl:template name="stripComma">
        <xsl:analyze-string select="normalize-space(.)" regex="^(.*)(,)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select="."/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>




</xsl:stylesheet>
