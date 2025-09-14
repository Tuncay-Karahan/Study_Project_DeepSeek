%*******************************************************************************
%
% LaTeX2e
%
\NeedsTeXFormat{LaTeX2e}
%*******************************************************************************

%*******************************************************************************
%
% package fontenc: Umlaute für pdf-Dokumente
%
\RequirePackage[T1]{fontenc}
%*******************************************************************************

%*******************************************************************************
%
% Message
%
\message{Style File für Prüfungen Hochschule Esslingen}
%*******************************************************************************

%*******************************************************************************
%
% Provide package 
%
\ProvidesPackage{pruefung}[2019/01/03]
%*******************************************************************************

%*******************************************************************************
%
% package ifthen: Optionen zum Erstellen von Varianten
%
\RequirePackage{ifthen}
%
\newboolean{Loesung}\setboolean{Loesung}{false}
\DeclareOption{Loesung}{\setboolean{Loesung}{true}}
\newboolean{Punkte}\setboolean{Punkte}{false}
\DeclareOption{Punkte}{\setboolean{Punkte}{true}}
\newboolean{Karos}\setboolean{Karos}{false}
\DeclareOption{Karos}{\setboolean{Karos}{true}}
%
\ProcessOptions\relax
%*******************************************************************************

%*******************************************************************************
%
% documentclass scrartcl
%
\LoadClass{scrartcl}
%*******************************************************************************

%*******************************************************************************
%
% package babel: Paket für Übersetzungen ins Deutsche (chapter->Kapitel, ... )
%
\RequirePackage[ngerman]{babel}
%*******************************************************************************

%*******************************************************************************
%
% package inputenc: Erweiterter Zeichensatz für Umlaute, ...
%
\RequirePackage[utf8]{inputenc}%
%*******************************************************************************

%*******************************************************************************
%
% package geometry: Seitenlayout
%
% Mit der zusätzlichen Option showframe wird die Geometry der Seite angezeigt.
%
%\RequirePackage[a4paper,includehead,showframe]{geometry}
%
\RequirePackage[a4paper,includehead]{geometry}
%*******************************************************************************

%*******************************************************************************
%
% package scrlayer-scrpage: Formatierung von Kopf- und Fußzeilen
%
\RequirePackage{scrlayer-scrpage}
%*******************************************************************************

%*******************************************************************************
%
% package mathtools: Paket für mathematische Symbole (includes amsmath)
%
%
% Mit der Option fleqn zusammen mit \mathindent werden Formeln linksbündig
% gesetzt. 
%
\RequirePackage[fleqn]{mathtools}
%\RequirePackage[fleqn]{amsmath}
\RequirePackage{amssymb}
%\RequirePackage{amsthm}
%*******************************************************************************

%*******************************************************************************
%
% package trfsigns: Paket für Transformationssymbole \laplace, \Laplace, ... 
%
\RequirePackage{trfsigns}
%*******************************************************************************

%*******************************************************************************
%
% package eurosym: Paket für Eurosymbol \EUR{}
%
\RequirePackage{eurosym}
%*******************************************************************************

%*******************************************************************************
%
% package graphicx: Grafiken einbinden
%
\RequirePackage{graphicx}
%*******************************************************************************

%*******************************************************************************
%
% package curves: Kurven zeichnen
%
\RequirePackage{curves}
%*******************************************************************************

%*******************************************************************************
%
% package xcolor: Farben
%
\RequirePackage{xcolor}
%*******************************************************************************

%*******************************************************************************
%
% package tikz: Schaubilder und karriertes Papier mit tikzpicture
%
\RequirePackage{tikz}
%*******************************************************************************

%*******************************************************************************
%
% package array: Paket zum Erweitern der Tabelleneigenschaften
%
\RequirePackage{array}
%*******************************************************************************

%*******************************************************************************
%
% package tabularx: Mehrere Spalten mit automatisch aufgeteilter selber Breite
%
\RequirePackage{tabularx} 
%*******************************************************************************

%*******************************************************************************
%
% package comment: Leere Befehle mit \excludecomment
%
\RequirePackage{comment}
%*******************************************************************************

%*******************************************************************************
%
% package enumitem: Numerierung bei enumerate fortsetzen
%
% \begin{enumerate}[series=XYZ]
% ...
% \end{enumerate}
% ...
% \begin{enumerate}[resume=XYZ]
% ...
% \end{enumerate}
%
\RequirePackage{enumitem}
%*******************************************************************************

%*******************************************************************************
%
% package calc: Umrechnen von Längenangaben \settototalheight
%
\RequirePackage{calc}% 
%*******************************************************************************

%*******************************************************************************
%
% package listings
%
\RequirePackage{listings}
%
%*******************************************************************************

%*******************************************************************************
%
% package totcount: Zähler für Gesamtpunktzahl \newtotcounter
%
\RequirePackage{totcount}
%
%*******************************************************************************

%*******************************************************************************
%
% package lastpage: Seitennummer der letzten Seite \pageref{LastPage}
%
\RequirePackage{lastpage}
%*******************************************************************************

%*******************************************************************************
%
% package etoolbox: Abfrage, ob LaTeX-Variablen leer sind mit \ifblank
%
\RequirePackage{etoolbox}
%
%*******************************************************************************

%*******************************************************************************
%
% package silence: Warnings filtern
%
\RequirePackage{silence}
%
% LastPage erzeugt eine Warnung, die bisher nicht anders beseitigt werden kann!
%
\WarningFilter{latex}{Reference `LastPage' on page 1 undefined}
%*******************************************************************************

%*******************************************************************************
%
% package karos: Karopapier \karos{Breite}{Hoehe}
%
\ifKaros
\RequirePackage[lightgray]{karos}
\fi
%*******************************************************************************

%*******************************************************************************
%
% Formatierungsanweisungen
%
% Standardschrift sans serif
%
\renewcommand{\familydefault}{\sfdefault} 
%
% Abstand zwischen Absätzen
%
\setlength{\parskip}\medskipamount
% 
% Absätze nicht einrücken
%
\setlength{\parindent}{0pt}
%
% Abgesetzte Formeln \[ ... \] um 10mm vom linken Rand einrücken
%
\setlength{\mathindent}{10mm}
%
%*******************************************************************************

%*******************************************************************************
%
% Kopfzeile
%
\newcommand{\Name}{\textbf{Name, Vorname \hfill Matrikelnummer}}%
\newcommand{\Loesungen}{\textbf{Prüfungsaufgaben mit Lösungen}}%
\newcommand{\Logo}{\includegraphics[width=0.6\linewidth]{HochschuleEsslingen_Logo_RGB_DE.png}}% [width=0.6\linewidth]
\newcommand{\Pruefungsfach}{\textbf{Prüfungsfach:}}%
\newcommand{\Semester}{\textbf{Semester:}}%
\newcommand{\Studiengaenge}{\textbf{Studiengänge:}}%
\newcommand{\Seite}{Seite:}%
\newcommand{\Von}{von}%
\newcommand{\Fachnummern}{\textbf{Fachnummer:}}%
\newcommand{\Dauer}{\textbf{Dauer: 90 Minuten}}%
\newcommand{\Dozenten}{\textbf{Dozenten:}}%
\newcommand{\Punktzahl}{\textbf{Punkte:}}%
\newcommand{\Hilfsmittel}{}%
\newcommand{\Hinweise}{}%
%
\newcommand{\Heading}{%
\setlength{\extrarowheight}{2mm}%
\begin{tabularx}{\textwidth}{@{}|X|p{50mm}|@{}}%
\hline%
& \\[-4mm]%
\ifLoesung%
\Loesungen%
\else%
\Name% 
\fi%
& \Logo\\%
\hline%
\Pruefungsfach & \Semester\\%
\hline%
\Studiengaenge & \textbf{\Seite \, \thepage \, \Von \, \pageref{LastPage}}\\%
\hline%
\end{tabularx}%
\bigskip%
}%
%
% Höhe der Kopfzeile berechnen
%
\newlength{\HeadingHeight}
\settototalheight{\HeadingHeight}{\Heading}
\addtolength{\HeadingHeight}{2\baselineskip}
%
% Abstand vom oberen Rand der Seite zur Kopfzeile justieren 
%
\newlength{\TopHeight}
\setlength{\TopHeight}{\HeadingHeight}
\addtolength{\TopHeight}{10mm}
%
% Layout der Seite festlegen
%
\newgeometry{head=\HeadingHeight,top=\TopHeight,width=175mm,headsep=0pt,bottom=15mm}
%
% Schriftart für Kopfzeile
%
\setkomafont{pageheadfoot}{\sffamily}
%
\pagestyle{scrheadings}
%
\ohead[]{}%
\chead[]{\Heading}%
\ihead[]{}%
\cfoot[]{}
\ifoot[]{}%
\ofoot[]{}%
%
% Erweiterung der Kopfzeile auf der ersten Seite
%
\AtBeginDocument{%
\setlength{\extrarowheight}{2mm}%
\vspace*{-11mm}%
\begin{tabularx}{\textwidth}{@{}|X|p{50mm}|@{}}%
\Fachnummern & \Dauer \\%
\hline%
\Dozenten & \Punktzahl \, \textbf{\total{Gesamtpunkte}} \\%
\hline%
\end{tabularx}%
\bigskip%
\ifdefempty{\Hilfsmittel}{}{%
\par%
\begin{tabularx}{\textwidth}{p{25mm}X}%
\textbf{Hilfsmittel:} & \Hilfsmittel%
\end{tabularx}%
\par%
}%
\ifdefempty{\Hinweise}{}{%
\par%
\begin{tabularx}{\textwidth}{p{25mm}X}%
\textbf{Hinweise:} & \Hinweise%
\end{tabularx}%
\par%
}%
\bigskip%
\par%
}%
%
%*******************************************************************************

%*******************************************************************************
%
% Aufgabe
%
% Zähler für Aufgaben
%
\newcounter{Aufgabe}
%
% Zähler für Gesamtpunktzahl
%
\newtotcounter{Gesamtpunkte}
%
% \begin{Aufgabe}
%   ...
% \end{Aufgabe}
%
\newenvironment{Aufgabe}[1][]%
{%
\ifblank{#1}{}{%
\addtocounter{Gesamtpunkte}{#1}%
}%
\renewcommand{\labelenumi}{\textbf{\alph{enumi})}}%
\renewcommand{\labelenumii}{\textbf{\alph{enumi}\arabic{enumii})}}%
\setlist{leftmargin=*}%
\setlist[1]{labelindent=\parindent}%
\stepcounter{Aufgabe}%
\textbf{Aufgabe \arabic{Aufgabe} \,%
\ifblank{#1}{}{%
(#1 Punkte) \,%
}%
}%
}%
%
%*******************************************************************************

%*******************************************************************************
%
% Lösung
%
\newlength{\MyParBoxHeight}%
\newsavebox\MyLstlistingBox%
%
% \Loesung{}{}
%
\newcommand{\Loesung}[2]{%
%
% Falls die Höhe für die Box nicht explizit angegeben wird,
% wird die maximale bis zum unteren Seitenende verfügbare Höhe ermittelt.
%
\ifblank{#1}{%
\setlength{\MyParBoxHeight}{\textheight}%
\advance\MyParBoxHeight by - \pagetotal%
\advance\MyParBoxHeight by - \lineskip%
\advance\MyParBoxHeight by - 5mm%
}{% else
\setlength{\MyParBoxHeight}{#1}%
}%
\ifLoesung%
\ifblank{#2}{%
\begingroup%
\setlength{\fboxsep}{-\fboxrule}%
\noindent\framebox[\linewidth]{\rule{0pt}{\MyParBoxHeight}}%
\endgroup%
}{%
\fbox{%
\parbox[t][\MyParBoxHeight]{0.985\linewidth}{% Hack, um "`Overfull hbox ..."' zu vermeiden ! 
%\color{gray}%
#2}%
}}%
\else%
\ifKaros%
\karos{\linewidth}{\MyParBoxHeight}%
\else%
\begingroup%
\setlength{\fboxsep}{-\fboxrule}%
\noindent\framebox[\linewidth]{\rule{0pt}{\MyParBoxHeight}}%
\endgroup%
\fi%
\fi%
}%
%
%*******************************************************************************

%*******************************************************************************
%
% Punkte
%
% \Punkte{}
%
\newcommand{\Punkte}[1]{%
\ifPunkte%
{\textcolor{red}{\fbox{#1}}}%
\fi%
}%
%
%*******************************************************************************
% EOF