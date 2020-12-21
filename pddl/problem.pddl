;; Problem definition
(define (problem problem-1)

  ;; Specifying the domain for the problem
  (:domain delivery-domain)

  ;; Objects definition
  (:objects
    ; DCs
    DC1
    DC2
    DC3
    ; Areas
    A11
    A12
    A21
    A22
    A31
    ; Parcels
    parcel1
    parcel2
    ; Vehicles
    LR1
    LR2
    SR1
    SR2
    SR3
  )

  ;; Intial state of problem 1
  (:init
    ;; Declaration of the objects
    ; We initialize the DCs
    (DIST-CENTER DC1)
    (DIST-CENTER DC2)
    (DIST-CENTER DC3)
    ; Areas
    (AREA A11)
    (AREA A12)
    (AREA A21)
    (AREA A22)
    (AREA A31)
    ; Parcel
    (PARCEL parcel1)
    (PARCEL parcel2)
    ; Vehicles
    (VEHICLE LR1)
    (VEHICLE LR2)
    (VEHICLE SR1)
    (VEHICLE SR2)
    (VEHICLE SR3)
    (long-range-vehicle LR1)
    (long-range-vehicle LR2)
    (short-range-vehicle SR1)
    (short-range-vehicle SR2)
    (short-range-vehicle SR3)
    ; Roads
    (connected DC1 DC2) (connected DC2 DC1)
    (connected A11 A12) (connected A12 A11)
    (connected DC1 A11) (connected A11 DC1)
    (connected DC1 A12) (connected A12 DC1)
    (connected A21 A22) (connected A22 A21)
    (connected DC2 A21) (connected A21 DC2)
    (connected DC2 A22) (connected A22 DC2)
    (connected DC1 DC3) (connected DC3 DC1)
    (connected DC2 DC3) (connected DC3 DC2)
    (connected DC3 A31) (connected A31 DC3)

    ;; Declaration of the predicates of the objects
    ; We set vehicles locations
    (is-vehicle-at LR1 DC1)
    (is-vehicle-at LR2 DC2)
    (is-vehicle-at SR1 DC1)
    (is-vehicle-at SR2 DC2)
    (is-vehicle-at SR3 DC3)
    ; We set the parcel initial position
    (is-parcel-at parcel1 A11)
    (is-parcel-at parcel2 A31)
  )

  ;; Goal specification
  (:goal
    (and
      ; We want parcel delivered to A22
      (is-parcel-at parcel1 A21)
      (is-parcel-at parcel2 A12)
    )
  )

)
