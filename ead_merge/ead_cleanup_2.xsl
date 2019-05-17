<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="xml" encoding="utf-8" indent="yes"/>


    <!-- Source will be output from ead_cleanup_1.xsl -->


    <xsl:param name="theDate">
        <xsl:value-of select="format-date(current-date(), 
            '[Y0001]-[M01]-[D01]')"/>
    </xsl:param>

    <xsl:variable name="my_name">ead_cleanup_2.xsl</xsl:variable>


    <!-- Identity template -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/">
        <!-- Some info about merge added at runtime.    -->
        <xsl:comment> 
    <xsl:text>File cleaned by </xsl:text><xsl:value-of select="$my_name"/><xsl:text> on </xsl:text>
    <xsl:value-of select="current-dateTime()"/>
        </xsl:comment>
        <xsl:text>&#xa;</xsl:text>

        <xsl:apply-templates/>

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



    <!-- Fix resolver links; minor fix to malformed FA URLs. -->
    <xsl:template match="eadid/@url">
        <xsl:attribute name="url">
            <xsl:analyze-string select="."
                regex="https?://www.columbia.edu/cgi-bin/cul/resolve\?clio(\d+)$">
                <xsl:matching-substring>https://library.columbia.edu/resolve/clio<xsl:value-of
                        select="regex-group(1)"/></xsl:matching-substring>
                <xsl:non-matching-substring>
                    <xsl:analyze-string select="." regex="/ead//">
                        <xsl:matching-substring>/ead/</xsl:matching-substring>
                        <xsl:non-matching-substring>
                            <xsl:value-of select="."/>
                        </xsl:non-matching-substring>
                    </xsl:analyze-string>
                </xsl:non-matching-substring>
            </xsl:analyze-string>
        </xsl:attribute>
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



    <!-- Select multi-paragraph notes, e.g., where
local-name()  = ('bioghist',  'scopecontent',  'accessrestrict',  'accruals',  'acqinfo',  'appraisal',  'altformavail',  'arrangement',  'bibliography',  'custodhist',  'langmaterial',  'note',  'odd',  'otherfindaid',  'prefercite',  'processinfo',  'relatedmaterial',  'separatedmaterial',  'userestrict') -->

    <xsl:template match="*[count(p) > 1]">

        <xsl:variable name="the_element" select="local-name(.)"/>
        <xsl:variable name="the_head" select="normalize-space(head)"/>

        <xsl:comment><xsl:value-of select="$theDate"/> - Split multi-paragraph <xsl:value-of select="$the_element"/> note into separate notes.</xsl:comment>
        
        <xsl:for-each-group select="*[not(self::head)]" group-starting-with="p">


            <xsl:element name="{$the_element}" xmlns="urn:isbn:1-931666-22-9">

                <xsl:if test="normalize-space($the_head)">
                    <head>
                        <xsl:value-of select="$the_head"/>
                    </head>
                </xsl:if>

                <xsl:apply-templates select="current-group()"/>

            </xsl:element>
        </xsl:for-each-group>
 
    </xsl:template>




    <!-- Physdesc with only text(), remove extraneous parens. at beginning and end. -->

    <xsl:template match="physdesc[not(*)]/text()">
        <xsl:analyze-string select="normalize-space(.)" regex="^\((.*)\)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <xsl:value-of select="."/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>

    </xsl:template>




    <!-- Fix problems with unittitle & unitdate. -->
    <xsl:template match="unittitle">

        <xsl:choose>

            <!--           Case 1: No unitdate.   -->
            <xsl:when test="not(unitdate)">
                <xsl:comment>Type 1</xsl:comment>
                <unittitle xmlns="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates/>
                    <!--<xsl:call-template name="stripComma"/>
                    -->
                </unittitle>
            </xsl:when>

            <!--           Case 2: Single unitdate at end (leave in place).   -->
            <xsl:when
                test="count(unitdate) = 1 and   unitdate[not(following-sibling::text()[normalize-space()])]">
                <xsl:comment>Type 2</xsl:comment>
                <unittitle xmlns="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates/>
                </unittitle>
            </xsl:when>

            <!--           Case 3: Text after a single unitdate.   -->
            <xsl:when
                test="unitdate and not(unitdate[2]) and text()[normalize-space()][preceding-sibling::unitdate]">
                <xsl:comment>Type 3</xsl:comment>
                <unittitle xmlns="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates mode="flatten"/>
                </unittitle>
                <xsl:for-each select="unitdate">
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:for-each>
            </xsl:when>


            <!--           Case 4: More than one unitdate, at any position.   -->
            <xsl:when test="unitdate[2]">
                <xsl:comment>Type 4</xsl:comment>
                <unittitle xmlns="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates mode="flatten"/>
                </unittitle>
                <xsl:for-each select="unitdate">
                    <xsl:copy>
                        <xsl:copy-of select="@*"/>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:for-each>
            </xsl:when>


            <!--           Case 5: Anything else?   -->
            <xsl:otherwise>
                <xsl:comment>** Warning: unexpected input **</xsl:comment>
                <unittitle xmlns="urn:isbn:1-931666-22-9">

                    <xsl:apply-templates/>
                </unittitle>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>


    <!-- strip trailing commas from unittitle text() if it is the last text() -->

    <xsl:template   match="unittitle[count(unitdate)&lt;2]/text()[substring(normalize-space(.),string-length(normalize-space(.))) = ',']">
        <xsl:call-template name="stripComma"/>
    </xsl:template>

    <!-- strip trailing commas from unittitle/title/text() where it precedes one and only unitdate -->

    <xsl:template        match="unittitle[count(unitdate)&lt;2]/title[following-sibling::unitdate]/text()[substring(normalize-space(.),string-length(normalize-space(.))) = ',']">
        <xsl:call-template name="stripComma"/>
    </xsl:template>


    <xsl:template match="unittitle/unitdate/text()[substring(normalize-space(.),string-length(normalize-space(.))) = ',']">
        <xsl:call-template name="stripComma"/>
    </xsl:template>


    <!-- Change @authfilenumber to @id, per https://archivesspace.atlassian.net/browse/ANW-152 -->
<!-- Note: This makes invalid EAD, but is meant to accommodate quirk of importer.   -->
    
<!--
    <xsl:template match="@authfilenumber">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
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


    <!-- Top containers: if there is no @label, copy @type to @label -->
    <xsl:template match="container[1][@type][not(@label)]">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="label"><xsl:value-of select="lower-case(@type)"/></xsl:attribute>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>


    <!-- Flatten arrangement notes -->

    <xsl:template match="arrangement" priority="2">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:if test="head">
                <xsl:copy-of select="head"/>
            </xsl:if>
            <p xmlns="urn:isbn:1-931666-22-9">
                <xsl:for-each select="p | list">
                    <xsl:apply-templates select="."/>
                    <xsl:text> </xsl:text>
                </xsl:for-each>
            </p>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="list[ancestor::arrangement]">
        <xsl:text> </xsl:text>
        <xsl:for-each select="item">
            <xsl:if test="position() > 1">; </xsl:if>
            <xsl:apply-templates/>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="p[ancestor::arrangement]">
        <xsl:apply-templates/>
    </xsl:template>
    

    <!-- Added for arrangement notes, but could be expanded to all text nodes(?)   -->
    <xsl:template match="p/text() | item/text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>

    
    

    <!-- Delete empty elements that won't import well -->

    <xsl:template match="scopecontent[not(normalize-space(.))][not(normalize-space(p))][not(@*)]"/>

    <xsl:template match="physdesc[not(normalize-space(.))][not(normalize-space(extent))][not(@*)]"/>

    <xsl:template match="unitdate[not(normalize-space(.))][not(@*)]"/>

    <xsl:template
        match="lb[not(normalize-space(.))] | genreform[not(normalize-space(.))] | physdesc[not(normalize-space(.))]"/>




    <!-- Strip trailing punctuation from specified text nodes  -->
    <xsl:template name="stripComma">
        <xsl:analyze-string select="." regex="^(.*),(\s*)$">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
                <xsl:value-of select="regex-group(2)"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <!-- in case match fails -->
                <xsl:value-of select="."/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>



    <!-- Convert structured data like unittitle/unitdate to only text. -->
    <xsl:template match="*" mode="flatten">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>


 
</xsl:stylesheet>
