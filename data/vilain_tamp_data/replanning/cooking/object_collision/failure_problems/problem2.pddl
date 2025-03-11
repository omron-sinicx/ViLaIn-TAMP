(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber potato - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (Robot b_bot)
        (PhysicalObject cucumber)
        (PhysicalObject potato)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At cucumber tray)
        (At potato plate)
    )

    (:goal
        (and
            (At cucumber plate)
        )
    )
)
