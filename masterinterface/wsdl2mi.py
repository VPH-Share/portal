__author__ = 'asaglimbeni'

from suds import client
import sys, shutil
from  wsdl2mi_utils import *


from django.core.management import execute_manager
import settings

def installService(wsdl_url):
    """

    Install Service script.
    It loads wsdl's services , methods and complextype , build directory and files structs.

    """

    base_path=os.path.abspath(os.path.dirname(__file__))

    ########
    ## Start Process Wsdl
    ########
    Client =client.Client(wsdl_url)

    #List of method
    methods=[]

    #Istance of Types , process the complessType.
    types=Types(Client)

    #List of service name
    services=[]

    #List of ports name
    ports=[]

    #Load wsdl's services, method and complexType
    #This section have to be optimized to process more service more port and check simpletype (all case)
    #Now we process only one service (the main) and only one port for service.

    for service in Client.wsdl.services:

        # parse suds wsdl object
        services.append(service.name)

        settingFile=file(base_path+'/settings.py','r')
        if settingFile.read().find(',\n    \'masterinterface.'+services[0])>0:
            settingFile.close()
            while True:
                print "\nService %s always exist, you can (D) Delete (R) Replace (A) Abort :\n" %services[0]
                response = sys.stdin.readline()
                if response[0] == 'D':

                    if os.path.exists(base_path+'/'+services[0]):
                        shutil.rmtree(base_path+'/'+services[0])

                    settingFile=file(base_path+'/settings.py','r')
                    newsettingFile=settingFile.read().replace(',\n    \'masterinterface.'+services[0]+'\'','')
                    settingFile.close()

                    settingFile=file(base_path+'/settings.py','w')
                    settingFile.write(newsettingFile)
                    settingFile.close()

                    UrlFile=file(base_path+'/urls.py','r')
                    newUrlFile=UrlFile.read().replace(',\n    url(r\'^'+services[0]+'/\', include(\'masterinterface.'+services[0]+'.urls\'))','')
                    UrlFile.close()
                    UrlFile=file(base_path+'/urls.py','w')
                    UrlFile.write(newUrlFile)
                    UrlFile.close()
                    exit(0)
                if response[0] == 'R':

                    if os.path.exists(base_path+'/'+services[0]):
                        shutil.rmtree(base_path+'/'+services[0])

                    settingFile=file(base_path+'/settings.py','r')
                    newsettingFile=settingFile.read().replace(',\n    \'masterinterface.'+services[0],'')
                    settingFile.close()

                    settingFile=file(base_path+'/settings.py','w')
                    settingFile.write(newsettingFile)
                    settingFile.close()

                    UrlFile=file(base_path+'/urls.py','r')
                    newUrlFile=UrlFile.read().replace(',\n    url(r\'^'+services[0]+'/\', include(\'masterinterface.'+services[0]+'.urls\'))','')
                    UrlFile.close()
                    UrlFile=file(base_path+'/urls.py','w')
                    UrlFile.write(newUrlFile)
                    UrlFile.close()
                    break
                if response[0] == 'A':
                    exit(0)

        settingFile.close()

        ports.append(service.ports[0].name)

        for method in service.ports[0].methods.values():

            # Initialize Method object
            m=Method(method.name)

            # Process Input types
            for part in method.soap.input.body.parts:
                ## there is a bug for not <element> tag
                #if part.element is None:
                #    continue
                #if part.name is not None and part.type is not None:
                #    m.input.append(part.name)
                #    types.appendType(part.name,part.type[0])
                #else:
                m.input.append(part.element[0])
                types.appendType(part.element[0],part.element[0])

            # Process Output type
            for part in method.soap.output.body.parts:
                ## there is a bug for not <element> tag
                #if part.element is None:
                #    continue
                #if part.name is not None and part.type is not None:
                #    m.output.append(part.name)
                #    types.appendType(part.name,part.type[0])
                #else:
                m.output.append(part.element[0])
                types.appendType(part.element[0],part.element[0])

            methods.append(m)


    ########
    ## End Process Wsdl
    ########


    ########
    ## Start Create dir struct and build file template.
    ########


    service_path=base_path+'/'+services[0]

    #Make directory
    if not os.path.exists(service_path):
        os.makedirs(service_path)

    if not os.path.exists(service_path+'/templates'):
        os.makedirs(service_path+'/templates')

    if not os.path.exists(service_path+"/templates/"+services[0]):
        os.makedirs(service_path+"/templates/"+services[0])

    #Istance of templates
    models=models_template()
    forms=forms_template()
    views=views_template(services[0])
    baseHtml=baseHtml_template()
    serviceHtml=serviceHtml_Template(services[0])
    urls=Urls_Template(services[0])
    indexHtml=indexHtml_Template(services[0])

    # Create types in models file

    for TypeName in types.types:

        models.addType(TypeName,types.types[TypeName])

    #Create a base html file
    baseHtml.addBaseHtml(services[0])

    #Process method and build file from template object
    ## TODO we need to process more services and more ports, how organize the struct of files and dir with  multiple services and ports?


    for method in methods:

        methodName= method.name

        #Append view on viewsClass
        views.addView(services[0],methodName,ports[0],wsdl_url)

        #Create a service html file.
        serviceHtml.addServiceHtml(methodName)

        urls.addUrl(methodName)

        #Create new form based on type input
        forms.addForm(methodName,method.input)


    ## Start create file
    modelsFile=file(service_path+'/models.py','w')
    modelsFile.write(models.getModelResult())
    modelsFile.close()

    formsFile=file(service_path+'/forms.py','w')
    formsFile.write(forms.getFormsResult())
    formsFile.close()

    viewsFile=file(service_path+'/views.py','w')
    viewsFile.write(views.getViewResult())
    viewsFile.close()

    baseHtmlfile=file(service_path+"/templates/"+services[0]+'/base.html','w')
    baseHtmlfile.write(baseHtml.getBaseHtmlResult())
    baseHtmlfile.close()

    indexHtmlFile=file(service_path+"/templates/"+services[0]+'/index.html','w')
    indexHtmlFile.write(indexHtml.getIndexHtml())
    indexHtmlFile.close()

    for serviceName in serviceHtml.name:
        serviceHtmlFile=file(service_path+"/templates/"+services[0]+"/"+serviceName+'.html','w')
        serviceHtmlFile.write(serviceHtml.getServiceHtml())
        serviceHtmlFile.close()

    initFile=file(service_path+'/__init__.py','w')
    initFile.close()

    urlsFile=file(service_path+'/urls.py','w')
    urlsFile.write(urls.getUrl())
    urlsFile.close()



    ## End create file

    ##Update setting and Urls on Master Inteface

    settingFile=file(base_path+'/settings.py','r')
    newsettingFile=settingFile.read().replace('\n\n    ##NEW_APP',',\n    \'masterinterface.'+services[0]+'\'\n\n    ##NEW_APP')
    settingFile.close()
    settingFile=file(base_path+'/settings.py','w')
    settingFile.write(newsettingFile)
    settingFile.close()

    ##Update setting and Urls on Master Inteface

    UrlFile=file(base_path+'/urls.py','r')
    newUrlFile=UrlFile.read().replace('\n\n    ##NEW_URL',',\n    url(r\'^'+services[0]+'/\', include(\'masterinterface.'+services[0]+'.urls\'))\n\n    ##NEW_URL')
    UrlFile.close()
    UrlFile=file(base_path+'/urls.py','w')
    UrlFile.write(newUrlFile)
    UrlFile.close()


    ########
    ## End Create dir struct and build file template.
    ########

if __name__ == '__main__':

    
    #    Main function. It starts install script with the wsdl url.
    
    print "Usage: %s <wsdl url>" % sys.argv[0]
    
    if len( sys.argv) < 2:
        print "\n please provide all inputs! "
        sys.exit(-1)


    ## http://www.webservicex.net/WeatherForecast.asmx?WSDL

    ## http://graphical.weather.gov/xml/SOAP_server/ndfdXMLserver.php?wsdl

    ## "http://www.webservicex.net/sendsmsworld.asmx?WSDL"
    wsdl_url= sys.argv[1]
    installService(wsdl_url)
    sys.argv.pop(1)
    sys.argv.append('syncdb')
    execute_manager(settings)
