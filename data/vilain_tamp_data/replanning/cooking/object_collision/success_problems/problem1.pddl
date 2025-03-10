(define (problem pick_and_place)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        cucumber tomato - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder other_plate - Location
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
        (At cucumber tray)
        (At tomato cutting_board)
    )

    (:goal
        (and
            (At cucumber cutting_board)
            (not (At tomato cutting_board))
        )
    )
)
