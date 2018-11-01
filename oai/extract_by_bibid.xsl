<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:output indent="yes"/>

    <!--    To run, transform an "AllRaw" AS harvest file, with bibid  as parameter. -->

    <!--    <xsl:param name="theBibID">xxxxxxx</xsl:param> -->
    <xsl:param name="bibid">xxxxxxxx</xsl:param>

    <xsl:template match="repository">
        <!--  Name the output file with metadata -->
            <xsl:copy>
                <xsl:copy-of
                    select="record[metadata/marc:collection/marc:record/marc:datafield[@tag='099']
                    /marc:subfield[@code='a'][text()=$bibid]]"
                />
            </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
