<?xml version="1.0" encoding="UTF-8"?>

<!-- This is intended to compare sets of ArchivesSpace OAI MARC exports from different sources, 
    e.g., different instances, that are presumptively the same content. 
    Only records that have the same BibID and date stamp are selected for inclusion. 
    The result documents can then be diff'd. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output indent="yes"/>

    <!-- Set two input files to form basis of comparison, and two output files for results from each. -->
    <xsl:variable name="devFile">path/to/dev/xmlfile</xsl:variable>
    <xsl:variable name="prodFile">path/to/prod/xmlfile</xsl:variable>

    <xsl:variable name="devOutFile">path/to/dev_extracted_xmlfile</xsl:variable>
    <xsl:variable name="prodOutFile">path/to/prod_extracted_xmlfile</xsl:variable>

    <xsl:template match="/">

        <!-- Build 1st result tree in the Dev output file. -->
        <xsl:result-document href="{$devOutFile}">

            <repository xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                <xsl:for-each select="document($devFile)/repository/record">

                    <xsl:apply-templates select="." mode="devRecord">
                        <xsl:with-param name="bibid">
                            <!-- get the Bib ID and pass to template-->
                            <xsl:value-of
                                select="metadata/marc:collection/marc:record/marc:datafield[@tag='099']/marc:subfield[@code='a']"
                            />
                        </xsl:with-param>
                        <xsl:with-param name="date">
                            <xsl:value-of select="header/datestamp"/>
                        </xsl:with-param>

                    </xsl:apply-templates>
                </xsl:for-each>
            </repository>

        </xsl:result-document>


        <!-- Build 2nd result tree in the Dev output file. -->
        <xsl:result-document href="{$prodOutFile}">

            <repository xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                <xsl:for-each select="document($prodFile)/repository/record">
                    <!-- Unfortunately this is time-consuming, as repeating the same process as before, in reverse. Should be a way to consolidate, but this works. (Cannot read the result doc from above in the same stylesheet.)-->
                    <xsl:apply-templates select="." mode="prodRecord">
                        <xsl:with-param name="bibid">
                            <!--   get the Bib ID -->
                            <xsl:value-of
                                select="metadata/marc:collection/marc:record/marc:datafield[@tag='099']/marc:subfield[@code='a']"
                            />
                        </xsl:with-param>
                        <xsl:with-param name="date">
                            <xsl:value-of select="header/datestamp"/>
                        </xsl:with-param>

                    </xsl:apply-templates>
                </xsl:for-each>
            </repository>

        </xsl:result-document>

    </xsl:template>


    <!-- Two templates to process each record. Could be consolidated? Only diff is the document() to test. -->
    <xsl:template match="record" mode="devRecord">
        <xsl:param name="bibid"/>
        <xsl:param name="date"/>
        <xsl:if
            test="document($prodFile)/repository/record[metadata/marc:collection/marc:record/marc:datafield[@tag='099']/marc:subfield[@code='a'][text()=$bibid]]/header/datestamp=$date">
            <xsl:copy-of select="."/>
        </xsl:if>
    </xsl:template>

    <xsl:template match="record" mode="prodRecord">
        <xsl:param name="bibid"/>
        <xsl:param name="date"/>
        <xsl:if
            test="document($devFile)/repository/record[metadata/marc:collection/marc:record/marc:datafield[@tag='099']/marc:subfield[@code='a'][text()=$bibid]]/header/datestamp=$date">
            <xsl:copy-of select="."/>
        </xsl:if>
    </xsl:template>


</xsl:stylesheet>
