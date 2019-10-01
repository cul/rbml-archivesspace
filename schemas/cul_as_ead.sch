<schema xmlns="http://www.ascc.net/xml/schematron">
    <ns prefix="ead" uri="urn:isbn:1-931666-22-9"/>
  
<!--Revised 9/2019 to conform to ArchivesSpace EADs as read by Finding Aid application. DH: 2019-09-18  -->
    
 
    
    <pattern name="Model of c element">
        <rule context="ead:c">
            <assert test="count(child::ead:did/ead:container) &lt;= 3" diagnostics="container">Warning: <name/> contains more than 3 container elements</assert>
            <assert test="count(child::ead:did/ead:unittitle) &lt;= 1" diagnostics="container">Warning: <name/> contains more than 1 unittitle element</assert>
        </rule>
        
        <!--  UPDATED RULE  -->
        <rule context="ead:container | ead:unittitle">
            <report test="not(normalize-space(.))" diagnostics="data">Warning: <name/> contains no text</report>
        </rule>

    </pattern>
    
    
    
    <pattern name="Elements Removed">

        <rule context="ead:unitdate">
            <assert test="ancestor::ead:did" diagnostics="structure"> ERROR <name/> NOT ALLOWED. <name/> is permitted as descendant of
                ead:did only</assert>
        </rule>
        
  
    </pattern>
    
    <pattern name="Attribute Values Controlled">
       
        
        <rule context="ead:language">
            <report test="contains(@langcode, ' ')" diagnostics="data">
                ERROR: Attribute @langcode should not contain any spaces
            </report>
        </rule>
    </pattern>


    <pattern name="dsc_structure">
        <rule context="ead:c[@level = 'series']">
            <report test="parent::ead:c[@level = 'series']" diagnostics="structure">
                WARNING: Series nested inside a series
            </report>
        </rule>
        <rule context="ead:c[@level = 'subseries']">
            <assert test="parent::ead:c[@level= 'series']" diagnostics="structure">
                WARNING: subseries NOT nested inside a series
            </assert>
        </rule>
        <rule context="ead:c[@level = 'file']">
            <assert test="parent::ead:c" diagnostics="structure">
                WARNING: file is a child of dsc. 
            </assert>
        </rule>
    </pattern>
    

    <pattern name="did_structure">
        <rule context="ead:archdesc/ead:did">
            <assert test="ead:langmaterial/ead:language[normalize-space(.)]" diagnostics="did">
                WARNING: <name/> must indicate language(s) of material (langmaterial/language). 
            </assert>
            <assert test="ead:origination" diagnostics="did">
                WARNING: <name/> must have origination as a child element. 
            </assert>
            <assert test="ead:unitdate" diagnostics="did">
                WARNING: <name/> must have a unitdate child element. 
            </assert>
            <assert test="ead:unitid" diagnostics="did">
                WARNING: <name/> must have a unitid child element. 
            </assert>
            <assert test="ead:physdesc" diagnostics="did">
                WARNING: <name/> must have a physdesc child element. 
            </assert>
        </rule> 
        
        <rule context="ead:archdesc/ead:did/ead:origination">
            <assert test="ead:persname or ead:corpname or ead:famname" diagnostics="did">
                WARNING: <name/> must have at least one of persname, corpname, or famname as child element. 
            </assert>
        </rule>
        
        
    </pattern>
    
    
    <pattern name="archdesc requirements">
        <rule context="ead:archdesc">
            <assert test="ead:scopecontent" diagnostics="archdesc">WARNING: archdesc should have scope and content element</assert>
            <assert test="ead:accessrestrict" diagnostics="archdesc">
                WARNING: <name/> must have at least one accessrestrict child element. 
            </assert>
        </rule>
        
    </pattern>
    
    
    <pattern name="empty_elements">
        <rule context="ead:persname | ead:corpname | ead:famname">
            <assert test="normalize-space(.)" diagnostics="data">WARNING: <name/> element is empty.</assert>
        </rule>
    </pattern>
    

    <diagnostics>

        <diagnostic id="structure">
            {structure}
        </diagnostic>

        <diagnostic id="container">
            {container}
        </diagnostic>
        
        <diagnostic id="data">
            {data}
        </diagnostic>
        
        <diagnostic id="did">
            {did}
        </diagnostic>
        
        <diagnostic id="archdesc">
            {archdesc}
        </diagnostic>
    </diagnostics>
</schema>