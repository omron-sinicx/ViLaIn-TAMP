; STREAMS FOR PDDL PLANNING DOMAIN (Manipulation)
;
; Contains cost functions for actions and streams for navigation and manipulation.
;
; Accompanying planning domain defined in the `domain.pddl` file.

(define
  (stream assembly_simple)

  (:stream compute-motion
    :inputs
    (?a ?p1 ?p2)
    :domain
    (and (Pose ?p1) (Pose ?p2) (Arm ?a))
    :outputs
    (?t)
    :certified
    (and (Motion ?a ?p1 ?t ?p2) (Traj ?t))
  )

  ; (:function (distance ?t) 
  ;   (Traj ?t))
)
