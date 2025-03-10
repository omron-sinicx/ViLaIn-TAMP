(define (problem slicing)
    (:domain cooking)
    (:objects
        a_bot b_bot - Robot
        tomato - PhysicalObject
        knife - Tool
        cutting_board tray plate knife_holder - Location
    )

    (:init
        (Robot b_bot)
        (Robot a_bot)
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
        (CanNotReach b_bot tomato)
        (At knife knife_holder)
        (At tomato tray)
    )

    (:goal
        (and
            (At tomato cutting_board)
        )
    )
)
