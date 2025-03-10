(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber tomato - PhysicalObject
        knife - Tool
        cutting_board tray plate plate2 knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (PhysicalObject cucumber)
        (PhysicalObject tomato)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)

        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)
        (Location other_plate)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (CanNotReach a_bot knife)

        (At knife knife_holder)
        (At cucumber plate)
        (At tomato plate2)
    )

    (:goal
        (and
            (At cucumber plate2)
            (not (At tomato plate2))
        )
    )
)
