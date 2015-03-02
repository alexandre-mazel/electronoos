<?php

	//
	// Script qui recoit des informations et les stocke
	//
	// params:
	//	
	// $host: l'host qui envoie l'info
	// $ip: son ip
	// $info: des infos optionnelles
    
    // sans parametre, ca affiche juste le contenu des infos
	

	if( !isset( $bAlmaFunctionDefined ) ) { include( "../../AlmaFunction.php3" ); }
	
	// recup params
	$strHost	= GetLineParam( 'host' );
	$strIP	= GetLineParam( 'ip' );
	$strInfo	= GetLineParam( 'info' );
    
    // read info
    $szFilename = "info.dat";
    $aInfoData = array();
    if( file_exists( $szFilename ) )
    {
        $pf=fopen( $szFilename, "rb" );
        if( $pf )
        {            
            $aInfoData = fread( $pf, 4096 );
            //~ $aInfoData = gzuncompress( $aInfoData, 600000 );
            $aInfoData = unserialize( $aInfoData );            
            print( "$aInfoData: " . $aInfoData );
            fclose( $pf );
        }
    }        
	
    if( $strHost == "" )
    {
        $nNbrData = count($aInfoData);
        print(" current info: nbr data: " . $nNbrData . "<br>\n" );
        if( $nNbrData < 1 )
        {
            print( "currently no data..." );
        }
        else
        {
            reset( $aInfoData );
            while (list ($key, $object) = each ($aInfoData) ) 
            {
                print( date( "d/m/Y H\hi", $object[0] ) . ": " . $object[1]. "@" . $object[2] . ":" . $object[3] . "<br>\n" );
            }        
        }
        return;
    }
    print( "storing info: host: " . $strHost .  ", ip: " . $strIP . ", info: '"  . $strInfo . "'<br>" );
    $aInfoData[] = array(mktime(), $strHost, $strIP, $strInfo );
    
    // ecris dans le fichier
    $pf = fopen( $szFilename, "wb" );		
    $aInfoData = serialize( $aInfoData );
    //~ $serialize( $aInfoData ) = gzcompress( serialize( $aInfoData ), 9 );
    fwrite( $pf, $aInfoData );
    fclose( $pf );
		
?>

