(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        apple carrot - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot a_bot)
        (Robot b_bot)
        (PhysicalObject apple)
        (PhysicalObject carrot)
        (Tool knife)

        (HandEmpty a_bot)
        (HandEmpty b_bot)
        (Location cutting_board)
        (Location tray)
        (Location plate)
        (Location knife_holder)

        (ToolHolder knife_holder)

        (isWorkspace cutting_board)

        (At knife knife_holder)
        (At apple tray)
        (At carrot plate)

        (isNotFree knife_holder)
        (isNotFree plate)
    )

    (:goal
        (and
            (At apple plate)
        )
    )
)
