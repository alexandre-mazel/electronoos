---
title: Demo - TP1 Test de diagram
description: Ecriture de code pour afficher des diagram
---

# A propos des diagrammes

## Introduction

Cette page est en endroit de démo pour tester les diagrammes et class diagram

!!! success "Objectifs"

    - me permettre de tester la création de diagramme et peut-être meme un peu de bloc code
    - Référence interessante: [:material-link: ressource des diagrammes](https://squidfunk.github.io/mkdocs-material/reference/diagrams/){:target="_blank"}
    

    
!!! danger "Attention au plagiat"

    Le plagiat est le fait de présenter comme sien un travail ou une idée empruntée à autrui.
    
    
    Dans le cas présent, vous remarquerez que ce site ressemble fortement à celui de Mr Yannick Mulot, mais bon il faut dire que son coté "graphiste" (no offense), le pousse à faire des rendu
    super propre qui font envie.
    
    
## Algorithme de mon assiduité au cours du mardi
    
On pourrait croire que mon algorithme est celui-ci, mais c'est faux

``` mermaid
graph LR
  A[Start] --> B{Est-ce que Yannick me regarde?};
  B -->|Oui| C[Avoir l'air de ne pas dormir];
  C --> D[Faire une blague];
  D --> B;
  B -->|Non| E[Dormir 10 secondes];
  E --> F[Aller taper la freebox pour qu'elle arrête de ronronner!]
  F-->B
```
<center>figure 1: Algorithme d'Alexandre </center>

## Stockage des exercices

``` mermaid
classDiagram
  Person <|-- Student
  Person <|-- QCM
  Person : *Int id
  Person : +String name
  Person : +String phoneNumber
  Person : +String emailAddress
  Person: +purchaseParkingPass()
  Address "1" <-- "0..1" Person:lives at
  class Student{
    +int studentNumber
    +int averageMark
    +isEligibleToEnrol()
    +getSeminarsTaken()
  }
  class QCM{
    +int salary
  }
  class Address{
    +String street
    +String city
    +String state
    +int postalCode
    +String country
    -validate()
    +outputAsLabel()  
  }
```

<center>figure 2: Stockage de mes données pour mes cours (non fini)</center>



## State machine
``` mermaid
sequenceDiagram
  autonumber
  Yannick->>Alexandre: Salut ca va bien?
  Alexandre->>Yannick: Ca va, et vous ?
  Yannick->> Alexandre: Cela se passe bien, j'ai réussi a finir ma préparation des cours pour demain pendant que mes éleves faisaient leur TP.
  Alexandre->>Yannick: Bravo Monsieur, vous gérez!
```



## Exemple d'état avec pleins d'options rarement utilisée.

``` mermaid
sequenceDiagram
  autonumber
  loop Healthcheck
      John->>John: Fight against hypochondria
  end
  Note right of John: Rational thoughts!
  John-->>Alice: Great!
  John->>Bob: How about you?
  Bob-->>John: Jolly good!
```